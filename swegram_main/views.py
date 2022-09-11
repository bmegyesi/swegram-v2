#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render

import json

from swegram_main.handle_texts.features import Texts

from .models import TextStats

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

from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


@require_http_methods(["PUT", "GET"])
@csrf_exempt
# @ensure_csrf_cookie
def update_texts_states(request):
    """
    Get the text states through put method
    Update the request.text_list given a single request
    """
    
    text_states = json.loads(request.body)['textStates']
    text_list = json.loads(request.body)['texts']
    for t in text_list:
        try:
            text = TextStats.objects.get(pk=t['pk'])
            text.activated = text_states[str(t['fields']['text_id'])]
            text.save()
            text_list.append(text)
        except Exception:
            pass 
    return JsonResponse({
      'updated text activity states': text_states
    })


from django.core import serializers    


class HandleTextView(View):
    http_method_names = ['get', 'delete']

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, text_id, *args, **kwargs):
        # text_attrs = "filename file_id file_size date_added \
        #               eligible activated id normalized has_label \
        #               meta_added labels lang".split()
        try:
            t = TextStats.objects.get(text_id=int(text_id))
            return JsonResponse(serializers.serialize('json', [t]), safe=False)
        except Exception:
            return JsonResponse({'error':'text %s is not found' % text_id})
    
    @method_decorator(ensure_csrf_cookie)
    def delete(self, request, text_id, *args, **kwargs):
        try:
            TextStats.objects.get(text_id=int(text_id)).delete()
            return JsonResponse({'success': 'Successfully deleted!'})
        except Exception:
            return JsonResponse({'failure': 'Text not found in the databse.'})
        
