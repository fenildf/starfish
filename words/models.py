# coding: utf-8
from django.db import models
from account.models import User
from consts import LEVEL_TRAN,STATUS_TRAN, Level
import uuid


class WordsManager(models.Manager):
    pass


class Words(models.Model):
    """单词总表"""
    word = models.CharField(max_length=50, default='', verbose_name="单词", unique=True)
    meaning = models.CharField(max_length=100, default='', verbose_name="中文意思")
    example = models.TextField(verbose_name="例句", null=True)
    synonym_id = models.IntegerField(default=0, verbose_name="近义词组id", db_index=True)

    class Meta:
        db_table = 'words'
        verbose_name_plural = verbose_name = "单词总表"

    @property
    def two_synonym(self):
        if not self.synonym_id:
            return []
        synonyms = list(Words.objects.filter(synonym_id=self.synonym_id).exclude(id=self.id).all()[:2])
        return synonyms


class WordsBase(models.Model):
    word = models.CharField(max_length=50, default='', verbose_name="单词", unique=True)
    meaning = models.CharField(max_length=100, default='', verbose_name="中文意思")
    example = models.TextField(verbose_name="例句", null=True)
    is_import = models.BooleanField(default=False, verbose_name="是否重点词汇")
    global_id = models.IntegerField(default=0, verbose_name="总表对应id", db_index=True)

    class Meta:
        abstract = True

    @property
    def two_synonym(self):
        word = Words.objects.get(id=self.global_id)
        return word.two_synonym

    @property
    def note(self):
        """获取5条单词笔记"""
        notes = list(WordNote.objects.filter(word_id=self.global_id).filter(is_share=True).all()[:5])
        return notes

    def save(self, *args, **kwargs):
        # 如果单词总表中没有，添加到总表中。
        try:
            global_word = Words.objects.get(word=self.word)
        except Exception:
            global_word = None
        if global_word:
            self.global_id = global_word.id
        else:
            word = Words.objects.create(word=self.word, meaning=self.meaning,
                                        example=self.example)
            self.global_id = word.id
        super(WordsBase, self).save(*args, **kwargs)


class CetFourWords(WordsBase):
    """四级词汇表"""

    class Meta(WordsBase.Meta):
        db_table = 'cet4_words'
        verbose_name_plural = verbose_name = "四级词汇"


class CetSixWords(WordsBase):
    """六级词汇"""

    class Meta(WordsBase.Meta):
        db_table = 'cet6_words'
        verbose_name_plural = verbose_name = "六级词汇"


class ToeftWords(WordsBase):
    """托福词汇"""

    class Meta(WordsBase.Meta):
        db_table = 'toeft_words'
        verbose_name_plural = verbose_name = '托福词汇'


class IeltsWords(WordsBase):
    """雅思词汇"""

    class Meta(WordsBase.Meta):
        db_table = 'ielts_words'
        verbose_name_plural = verbose_name = '雅思词汇'


class ReciteRecord(models.Model):
    """背诵记录"""
    word_id = models.IntegerField(default=0, verbose_name="单词id", db_index=True)
    level = models.IntegerField(default=0, choices=LEVEL_TRAN.items(), verbose_name="单词水平")
    user_id = models.IntegerField(default=0, verbose_name="用户id", db_index=True)
    status = models.IntegerField(default=0, choices=STATUS_TRAN.items(), verbose_name="背诵状态 0:还没背,1:背诵中,2:已掌握")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def word(self):
        return CetFourWords.objects.get(pk=self.word_id).word
    word.short_description = "单词"
    word = property(word)

    def user_email(self):
        return User.objects.get(pk=self.user_id).email
    user_email.short_description = "用户邮箱"
    user_email = property(user_email)

    class Meta:
        db_table = "recite_record"
        ordering = ['-update_time']
        verbose_name_plural = verbose_name = '背诵记录表'


class WordNote(models.Model):
    """单词笔记"""
    word_id = models.IntegerField(default=0, verbose_name="单词id", db_index=True)
    user_id = models.IntegerField(default=0, verbose_name="用户id", db_index=True)
    content = models.TextField(default='', verbose_name="笔记内容")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    is_share = models.BooleanField(default=False, verbose_name="笔记是否共享")

    def word(self):
        return Words.objects.get(pk=self.word_id).word
    word.short_description = "单词"
    word = property(word)

    def user_email(self):
        return User.objects.get(pk=self.user_id).email
    user_email.short_description = "用户邮箱"
    user_email = property(user_email)

    @property
    def user_nickname(self):
        return User.objects.get(pk=self.user_id).nickname

    def content_cut(self):
        """获取笔记内容的前15个字符"""
        return self.content[:15]+'...'
    content_cut.short_description = "评论"
    content_cut = property(content_cut)

    class Meta:
        db_table = 'word_note'
        verbose_name_plural = verbose_name = "笔记"


class SynonymGroup(models.Model):
    """近义词"""
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "synonym_group"
        verbose_name_plural = verbose_name = "近义词组"

