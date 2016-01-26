from django.db import models
from django.utils.text import slugify
from django.forms import ModelForm, HiddenInput
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse
from django import forms
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver


class ItemAuthor(models.Model):
	author = models.CharField(max_length=48)
	authorslug = models.SlugField(max_length=48)
	
	def __str__(self):
		return self.author
		
	def save(self,*args,**kwargs):
		if not self.pk:
			self.authorslug = slugify(self.author)
		super(ItemAuthor,self).save(*args,**kwargs)
		
	class Meta:
		verbose_name = "Item Author"
		verbose_name_plural = "Item Authors"
	
class ItemTitle(models.Model):
	author = models.ForeignKey(ItemAuthor)
	title = models.CharField(max_length=64)
	rating = models.DecimalField(max_digits=2, decimal_places=1)
	
	def __str__(self):
		return self.title
		
	class Meta:
		verbose_name = "Item Title"
		verbose_name_plural = "Item Titles"

class BookBucket(models.Model):
	BOOK = 'book'
	VIDEO = 'video'
	AUDIOBOOK = 'book'
	TYPE_CHOICES = (
		(BOOK, 'Book'),
		(VIDEO, 'Movie'),
		(AUDIOBOOK, 'Audiobook'),
	)
	
	DNC = "9"
	ONE = "1"
	TWO = "2"
	THREE = "3"
	FOUR = "4"
	FIVE = "5"
	
	RATING_CHOICES = (
		(DNC, 'On Reading/Viewing List'),
		(ONE, '1 - Would Not Recommend'),
		(TWO, '2'),
		(THREE, '3'),
		(FOUR, '4'),
		(FIVE, '5 - Excellent'),
	)
	
	user = models.ForeignKey(User)
	title = models.ForeignKey(ItemTitle)
	read = models.NullBooleanField()
	type = models.CharField(max_length=5, choices=TYPE_CHOICES)
	rating = models.CharField(max_length=1, choices=RATING_CHOICES)
	tags = TaggableManager()
	
	def get_absolute_url(self):
		return(reverse('workroom:bucket_item_view', kwargs={"itemID":self.pk}))

	def __str__(self):
		return self.title.title
		
	class Meta:
		verbose_name = "Item"
		verbose_name_plural = "Items"
		
@receiver(pre_delete, sender=BookBucket)
def clear_post_tags(sender, instance, **kwargs):
	instance.tags.clear()		
