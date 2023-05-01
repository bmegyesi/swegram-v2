#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from django.http import JsonResponse
from swegram_main import config
from swegram_main.models import TextStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_text_list(request, category=False):
    if request.body:
        payload = json.loads(request.body)
        lang = payload.get('lang')
        text_list = []
        for t in payload.get('texts', {}).get(lang, []):
            try:
                t = TextStats.objects.get(pk=t['pk'])
                if t.activated:
                    text_list.append(t)
            except Exception as err:
                logger.error(f"Failed to get text list: {str(err)}")
        if category:
            if category == 'normalized' or category == 'norm':
                text_list = [ text for text in text_list if text.normalized ]
            elif category == 'parsed' or category == 'lemma':
                text_list = [ text for text in text_list if text.parsed ]
        
        return text_list
    return []
    


def fetch_current_sentences(request, text_id, page):
    """
    The default size to show the sentences for visualisation is 20
    """
    for text in get_text_list(request):
        if str(text.id) == str(text_id):
            sentences = text.sentences[int(page-1) * config.PAGE_SIZE, int(page) * config.PAGE_SIZE]
            return JsonResponse({'current_sentences': sentences})
    return JsonResponse({'current_sentences': []})

def mean(numbers):
    """if numbers not exist, we return 0"""
    return round(sum(numbers)/max(len(numbers),1), 2)
    #return round(float(sum(numbers)) / max(len(numbers), 1), 2)

def median(numbers):
    """if numbers not exist, we return 0"""
    if not numbers: return 0
    if len(numbers) % 2 == 1: 
        return sorted(numbers)[len(numbers)//2]
    else:
        a,b = sorted(numbers)[len(numbers)//2], numbers[len(numbers)//2-1]
        return round((a+b)/2, 2)
        