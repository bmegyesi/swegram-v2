#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render

from swegram_main.handle_texts.features import Texts


from .models import TextStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_swedish(request):
    if request.session.get('language') == 'en':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'sv'

    context = {'url': __root_path()}
    return render(request, 'start_sv.html', context)

def start_english(request):
    from django.core.management import call_command
    call_command('createcachetable', database='default')
    if request.session.get('language') == 'sv':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'en'
    request.session.modified = True

    context = {'url': __root_path()}
    return render(request, 'swegram_main_english/start_en.html', context)

def swegram_main_swedish(request):
    if request.session.get('language') == 'en':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'sv'
    if request.session.get('text_list'):
        request.session['text_list'] = sum([text for text in request.session['text_list'] if text.activated], [])
   
    context = {'url': __root_path()}
    return render(request, "swegram_main/main.html", context)

def swegram_main_english(request):
    if request.session.get('language') == 'sv':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'en'
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {'url': __root_path()}
    return render(request, "swegram_main_english/main.html", context)

def __root_path():
    if settings.PRODUCTION:
        return ''
    elif settings.BETA:
        return ''
    return ''
