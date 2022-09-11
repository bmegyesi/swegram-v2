from django.urls import re_path
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views
from .handle_texts.upload_file import upload_annotated_file, annotate_uploaded_file
from .handle_texts.helpers import  update_texts, automatic_delete
from .handle_texts.visualize import fetch_current_sentences
from .handle_texts.features import get_features, get_chosen_texts_info, get_type, fetch_overview_features
from .handle_texts.download import download_texts, download_stats_file

app_name = 'swegram'

urlpatterns = [
    url(r'^$', views.start_swedish, name='start_swedish'),
    url(r'^en/$', views.start_english, name='start_english'),    
    url(r'^swedish/.*$', views.swegram_main_swedish, name='swegram_main_swedish'),
    url(r'^english/.*$', views.swegram_main_english, name='swegram_main_english'),

    # link to get access to version 2 of swegram
    url(r'^v2/.*$', TemplateView.as_view(template_name="index.html")),
    
    # used for text uploading and annotation
    re_path(r'^upload_annotate/(?P<lang>(en|sv){1})', annotate_uploaded_file),
    re_path(r'^upload/(?P<lang>(en|sv){1})', upload_annotated_file),
    
    # used to get the latest states of selected texts with basic text info
    url(r'^update_texts/$', update_texts),

    # triggered when there is a change of text selection
    url(r'^api/updatestates', views.update_texts_states), # change the activity states of the texts
    
    # to delete text from the database
    re_path(r'^api/text/(?P<text_id>\d+)', views.HandleTextView.as_view()),
   
    # This url is used to get text info when displaying statistics (length, frequency)
    re_path(r'^get_text_stats/$', get_chosen_texts_info),
    
    # used for visualisation of statistics
    re_path(r'^(?P<category>(form|norm|lemma){1})/(?P<tagset>(upos|xpos){1})', get_type),
    re_path(r'^(?P<category>(form|norm|lemma){1})/(?P<tagset>(upos|xpos){1})/length', get_type),
    re_path(r'^features/(?P<level>(text|para|sent){1})/(?P<page>\d+)', get_features),
    re_path(r'^overview/(?P<level>(text|para|sent){1})', fetch_overview_features),

    # used for visualisation of texts
    re_path(r'^visualise_text/(?P<text_id>\d+)/(?P<page>\d+)/$', fetch_current_sentences),

    # download all texts or statistics that are activated 
    re_path(r'^download_text/$', download_texts),
    re_path(r'^download_stats/$', download_stats_file),

    # delete the texts in database longer than the given threshold.
    url(r'^automatic_delete/$', automatic_delete)
]
