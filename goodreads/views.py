from goodreads import client, session
from goodreads import owned_book as gr_owned_book
from goodreads import book as gr_book_instance
from goodreads import user as gr_user
from goodreads import author as gr_author
from goodreads import request as gr_request
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import xmltodict

grKey = settings.GR_KEY
grSecret = settings.GR_SECRET

grClient = client.GoodreadsClient(grKey,grSecret)

def goodReadsOAUTH_verification(request):
	try:
		gcURL = grClient.authenticate()
		request.session['grSessionInfo'] = grClient
		return HttpResponseRedirect(gcURL)
	except:
		return render(request, 'gr-django/oauth_error.html', {'error':'OAUTH validation failed.','page_title':'OAUTH Error'})

def goodReadsOAUTH_handler(request):
	if request.method == "GET" and ('authorize' in request.GET):
		if request.GET['authorize'] == '1':
			try:
				grClient.session.oauth_finalize()
			except:
				try:
					grClient.session.oauth_resume()
					grClient.session.oauth_finalize()
				except:
					return render(request, 'gr-django/oauth_error.html', {'error':'OAUTH verification failed, please try again.','page_title':'OAUTH Error'})
			try:
				gc_user = grClient.auth_user()
				gc_user = grClient.user(user_id=gc_user.gid)
			except:
				return render(request, 'gr-django/oauth_error.html', {'error':'No authorized GoodReads user was found in this session, please try again.','page_title':'OAUTH Error'})
			if gc_user:
				try:
					request.user.grimport
				except ObjectDoesNotExist:
					new_import = grImport(patron=request.user)
					new_import.save()
				import string
				user_owned_books = gc_user._client.session.get("owned_books/user/%s.xml" % gc_user.gid,{'page': 1, 'format': 'xml'})
				if not user_owned_books is None:
					user_owned_books = user_owned_books['owned_books']
					book_count = 0
					if not user_owned_books is None:
						try:
							for key in user_owned_books:
								for gc_book in user_owned_books[key]:
									gr_author_name = gc_book['book']['authors']['author']['name']
									temp_slug = slugify(gr_author_name)
									gr_book_title = string.capwords(gc_book['book']['title'])
									author_id = ItemAuthor.objects.filter(authorslug=temp_slug)
									if not author_id:
										author_id = ItemAuthor(author=gr_author_name)
										author_id.save()
										title_id = ItemTitle(author=author_id,title=gr_book_title,rating=float(gc_book['review']['rating']))
										title_id.save()
									else:
										author_id = author_id[0]
										title_info = ItemTitle.objects.filter(author=author_id, title=gr_book_title)
										if not title_info:
											title_id = ItemTitle(author=author_id,title=gr_book_title,rating=float(gc_book['review']['rating']))
											title_id.save()
										else:
											title_id = title_info[0]
											title_id.save()
									try:
										test = request.user.bookbucket_set.get(title=title_id)
									except:
										temp = BookBucket(user=request.user,title=title_id,read=True,type='book',rating=float(gc_book['review']['rating']))
										temp.save()
										temp.tags.add("goodreads import")
										setRating(title_id)
										UpdateTags(temp)
							return HttpResponseRedirect(reverse('workroom:success', kwargs={'user':request.user.username,'type':'goodreads-import'}))
						except TypeError:
							return render(request, 'gr-django/oauth_error.html', {'error':'Goodreads returned information in a format this application does not recognize; this generally occurs when your owned books shelf only contains a single item. Please add another item on GoodReads and try importing again.','page_title':'OAUTH Error'})
					else:
						return render(request, 'gr-django/oauth_error.html', {'error':'No owned books were returned.','page_title':'OAUTH Error'})
				else:
					return render(request, 'gr-django/oauth_error.html', {'error':'No owned books were returned.','page_title':'OAUTH Error'})
		else:
			return render(request, 'gr-django/oauth_error.html', {'error':'This site was denied OAUTH permission for this account.','page_title':'OAUTH Error'})
	else:
		return render(request, 'workroom/oauth_error.html', {'error':'This site was denied OAUTH permission for this account.','page_title':'OAUTH Error'})
