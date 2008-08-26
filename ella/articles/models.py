from datetime import datetime

from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from ella.db.models import Publishable
from ella.core.models import Category, Author, Source
from ella.core.managers import RelatedManager
from ella.core.cache import get_cached_list
from ella.photos.models import Photo


class InfoBox(models.Model):
    """Defines embedable text model."""
    title = models.CharField(_('Title'), max_length=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    content = models.TextField(_('Content'))

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Info box')
        verbose_name_plural = _('Info boxes')

class Article(Publishable, models.Model):
    """Defines article model."""
    # Titles
    title = models.CharField(_('Title'), max_length=255)
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)

    # Contents
    perex = models.TextField(_('Perex'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    # Main Photo to Article
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    objects = RelatedManager()

    @property
    def content(self):
        """Returns first item from ArticleContents linked to current article"""
        if not hasattr(self, '_contents'):
            self._contents = get_cached_list(ArticleContents, article=self)
        if self._contents:
            return self._contents[0]
        else:
            return None

    def get_description(self):
        """Overrides Publishable.get_description method"""
        return self.perex

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ('-created',)

    def __unicode__(self):
        return self.title

    def article_age(self):
        """Returns time since article was created"""
        return timesince(self.created)
    article_age.short_description = _('Article Age')

    def get_text(self):
        return self.content.content



class ArticleContents(models.Model):
    """Defines article's contents model.

    One article can have multiple contets. (1:N)"""
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    title = models.CharField(_('Title'), max_length=200, blank=True)
    content = models.TextField(_('Content'))

    class Meta:
        verbose_name = _('Article content')
        verbose_name_plural = _('Article contents')
        #order_with_respect_to = 'article'

    def __unicode__(self):
        return self.title

