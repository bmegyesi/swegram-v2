from __future__ import unicode_literals
from django.db import models

"""
note: JSONField was previously used to store dict-type data. 
Since this field is not supported until it meets the following criteria:
1: PostgreSQL ≥ 9.4 
2: Psycopg2 ≥ 2.5.4

In order to get rid of this incompatibility, here use TextField to replace JSONField
and use json.dumps and json.loads to parse. 
"""


# This is used to check if an uploaded file has previously been annotated,
# if the md5 matches we can determine whether it's been normalized or not
class UploadedFile(models.Model):

    class Meta:
       app_label = "swegram_main"

    md5_checksum = models.CharField(max_length=32, blank=False, primary_key=True)
    normalized = models.BooleanField(blank=False)


# class Text is a solution to solve the problem of selecting and update the activity of selected texts on real time
class TextStatsModel(models.Model):
    
    class Meta:
        app_label = "swegram_main"
    
    # primary key will be unique to keep same text with different creation
    text_id             = models.CharField(max_length=64)  # md5_checksum
    language            = models.CharField(max_length=16)
    filename            = models.CharField(max_length=64)
    filesize            = models.IntegerField(blank=0, null=True)
    states              = models.JSONField(null=True)
    labels              = models.JSONField(null=True)
    number_of_paragraphs    = models.IntegerField(blank=0, null=True)
    number_of_sentences     = models.IntegerField(blank=0, null=True)

    activated    =   models.BooleanField(default=False)
    date_added   =   models.DateTimeField(auto_now_add=True)


    @property
    def has_label(self) -> bool:
        return True if self.labels else False

    @property
    def normalized(self) -> bool:
        return self.states.normalized

    @property
    def tagged(self) -> bool:
        return self.states.tagged

    @property
    def parsed(self) -> bool:
        return self.states.parsed

    def __repr__(self):
        return self.filename


class TextModel(models.Model):

    class Meta:
        app_label = "swegram_main"

    stats               = models.OneToOneField(TextStatsModel, on_delete=models.CASCADE)

    # features
    # general             = models.JSONField(null=True)
    # readability         = models.JSONField(null=True)
    # morph               = models.JSONField(null=True)
    # morph_average       = models.JSONField(null=True)
    # lexical             = models.JSONField(null=True)
    # lexical_average     = models.JSONField(null=True)
    # syntactic           = models.JSONField(null=True)
    # syntactic_average   = models.JSONField(null=True)

    general             = models.TextField(null=True)
    readability         = models.TextField(null=True)
    morph               = models.TextField(null=True)
    morph_average       = models.TextField(null=True)
    lexical             = models.TextField(null=True)
    lexical_average     = models.TextField(null=True)
    syntactic           = models.TextField(null=True)
    syntactic_average   = models.TextField(null=True)
    content             = models.TextField(null=True)

    def __str__(self):
        return self.content


class ParagraphModel(models.Model):

    class Meta:
        app_label = "swegram_main"

    text = models.ForeignKey(TextModel, on_delete=models.CASCADE)

    # general             = models.JSONField(null=True)
    # readability         = models.JSONField(null=True)
    # morph               = models.JSONField(null=True)
    # morph_average       = models.JSONField(null=True)
    # lexical             = models.JSONField(null=True)
    # lexical_average     = models.JSONField(null=True)
    # syntactic           = models.JSONField(null=True)
    # syntactic_average   = models.JSONField(null=True)

    general             = models.TextField(null=True)
    readability         = models.TextField(null=True)
    morph               = models.TextField(null=True)
    morph_average       = models.TextField(null=True)
    lexical             = models.TextField(null=True)
    lexical_average     = models.TextField(null=True)
    syntactic           = models.TextField(null=True)
    syntactic_average   = models.TextField(null=True)

    content             = models.TextField(null=True)

    def __str__(self):
        return self.content


class SentenceModel(models.Model):

    class Meta:
        app_label = "swegram_main"
    
    text        = models.ForeignKey(TextModel, on_delete=models.CASCADE)
    paragraph   = models.ForeignKey(ParagraphModel, on_delete=models.CASCADE)
    
    text_index  = models.CharField(max_length=512)
    # types       = models.JSONField(null=True)
    types       = models.TextField(null=True)
    ud_tree     = models.BooleanField(default=True)

    # general     = models.JSONField(null=True)
    # readability = models.JSONField(null=True) 
    # morph       = models.JSONField(null=True) 
    # lexical     = models.JSONField(null=True)
    # syntactic   = models.JSONField(null=True)

    general     = models.TextField(null=True)
    readability = models.TextField(null=True)
    morph       = models.TextField(null=True)
    lexical     = models.TextField(null=True)
    syntactic   = models.TextField(null=True)

    content     = models.TextField(null=True)

    def __str__(self):
        return self.content


class TokenModel(models.Model):
    
    class Meta:
        app_label = "swegram_main"
    
    sentence = models.ForeignKey(SentenceModel, on_delete=models.CASCADE)
  
    compound_originals   = models.BooleanField(default=False)
    normalized           = models.BooleanField(default=False)
    token_index          = models.CharField(max_length=512)
    text_index           = models.CharField(max_length=512)
    form                 = models.CharField(max_length=512, default="_")
    norm                 = models.CharField(max_length=512, default="_", blank=True)
    lemma                = models.CharField(max_length=512, default="_", blank=True)
    upos                 = models.CharField(max_length=512, default="_", blank=True)
    xpos                 = models.CharField(max_length=512, default="_", blank=True) 
    feats                = models.CharField(max_length=512, default="_", blank=True) 
    ufeats               = models.CharField(max_length=512, default="_", blank=True) 
    head                 = models.CharField(max_length=512, default="_", blank=True) 
    deprel               = models.CharField(max_length=512, default="_", blank=True) 
    deps                 = models.CharField(max_length=512, default="_", blank=True) 
    misc                 = models.CharField(max_length=512, default="_", blank=True) 
    path                 = models.CharField(max_length=512, default="", blank=True)
    highlight            = models.CharField(max_length=512, default="", blank=True)
    length               = models.IntegerField(blank=True, null=True) 
    dep_length           = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.form

