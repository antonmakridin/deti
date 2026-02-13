import re
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils import timezone
from datetime import date

class Characteristic(models.Model):
    # Таблица наименований характеристик
    name = models.CharField(max_length=255, verbose_name='Наименование характеристики')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class CharacteristicValue(models.Model):
    # Таблица значений характеристик
    characteristic_id = models.IntegerField(verbose_name='ID характеристики')
    value = models.CharField(max_length=255, verbose_name='Значение')
    
    class Meta:
        verbose_name = 'Значение характеристики'
        verbose_name_plural = 'Значения характеристик'
        ordering = ['characteristic_id', 'value']
        # # Уникальность значения в рамках характеристики
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['characteristic_id', 'value'],
        #         name='unique_characteristic_value'
        #     )
        # ]
    
    def __str__(self):
        # Получаем имя характеристики по ID
        try:
            char = Characteristic.objects.get(id=self.characteristic_id)
            return f"{char.name}: {self.value}"
        except Characteristic.DoesNotExist:
            return f"Характеристика #{self.characteristic_id}: {self.value}"

class Person(models.Model):
    # Основная таблица детей
    name = models.CharField(max_length=255, verbose_name='Имя')
    photo = models.ImageField(
        upload_to='catalog/people/', 
        verbose_name='Фотография',
        blank=True,
        null=True)
    birth_date = models.CharField(
        max_length=7, 
        verbose_name='Дата рождения (мм-гггг)',
        help_text='Формат: мм-гггг (например: 02-2016)'
    )
    description = models.TextField(verbose_name='Описание ребенка')
    
    # Хранение ID характеристик
    characteristics_ids = models.JSONField(
        default=list,
        verbose_name='ID значений характеристик',
        help_text='Список ID значений характеристик',
        blank=True,
        null=True
    )
    
    # Хранение ID братьев/сестер
    siblings_ids = models.JSONField(
        default=list,
        verbose_name='ID братьев/сестер',
        help_text='Список ID братьев/сестер',
        blank=True,
        null=True
    )
    
    # Дополнительные поля
    photo_publish_date = models.DateField(default=timezone.now, verbose_name='Дата публикации фотографии')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        verbose_name = 'Ребенок'
        verbose_name_plural = 'Дети'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:person_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        # Валидация формата даты рождения
        super().clean()
        if self.birth_date:
            # Проверяем формат мм-гггг
            pattern = r'^(0[1-9]|1[0-2])-\d{4}$'
            if not re.match(pattern, self.birth_date):
                raise ValidationError({
                    'birth_date': 'Введите дату в формате мм-гггг (например: 05-2010)'
                })
    
    def get_age(self):
        # Рассчитываем возраст на основе даты рождения
        if not self.birth_date:
            return None
        
        try:
            # Парсим месяц и год из строки
            month, year = map(int, self.birth_date.split('-'))
            
            today = date.today()
            age = today.year - year
            
            if today.month < month or (today.month == month and today.day < 1):
                age -= 1
                
            return age
        except (ValueError, AttributeError):
            return None
    
    def get_birth_date_display(self):
        # Возвращаем отформатированную дату рождения
        if not self.birth_date:
            return ""
        
        try:
            month, year = self.birth_date.split('-')
            months_ru = {
                '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
                '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
                '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
            }
            return f"{months_ru.get(month, month)} {year} года"
        except ValueError:
            return self.birth_date
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def get_siblings_info(self):
        # Выводим братьев/сестер
        if not self.siblings_ids:
            return "Нет братьев/сестер"
        
        siblings = Person.objects.filter(
            id__in=self.siblings_ids,
            is_published=True
        )
        
        if not siblings:
            return "Нет братьев/сестер"
        
        siblings_info = []
        for sibling in siblings:
            age = sibling.get_age()
            if age == 1:
                years_old = 'год'
            elif age == 2 or age == 3 or age == 4:
                years_old = 'года'
            else:
                years_old = 'лет'
            siblings_info.append(f"<a href='/catalog/{sibling.id}/'>{sibling.name} ({age} {years_old})</a>")
        
        return ",<br>".join(siblings_info)
    
    @classmethod
    def filter_by_age_range(cls, min_age=None, max_age=None):
        # Фильтрация по диапазону возрастов
        persons = cls.objects.filter(is_published=True)
        
        if min_age is None and max_age is None:
            return persons
        
        filtered_ids = []
        for person in persons:
            age = person.get_age()
            if age is not None:
                if min_age is not None and max_age is not None:
                    if min_age <= age <= max_age:
                        filtered_ids.append(person.id)
                elif min_age is not None:
                    if age >= min_age:
                        filtered_ids.append(person.id)
                elif max_age is not None:
                    if age <= max_age:
                        filtered_ids.append(person.id)
        
        return persons.filter(id__in=filtered_ids)
    
    def get_characteristics_dict(self):
        # Возвращаем характеристики в виде словаря
        if not self.characteristics_ids:
            return {}
        
        # Получаем значения характеристик по их ID
        char_values = CharacteristicValue.objects.filter(id__in=self.characteristics_ids)
        
        characteristics_dict = {}
        for char_value in char_values:
            # Получаем имя характеристики по characteristic_id
            try:
                char = Characteristic.objects.get(id=char_value.characteristic_id)
                char_name = char.name
            except Characteristic.DoesNotExist:
                char_name = f"Характеристика #{char_value.characteristic_id}"
            
            if char_name not in characteristics_dict:
                characteristics_dict[char_name] = []
            
            characteristics_dict[char_name].append(char_value.value)
        
        return characteristics_dict
    
class PersonCharacteristic(models.Model):
    # Таблица связей детей с характеристиками
    person_id = models.IntegerField(verbose_name='ID ребенка')
    characteristic_value_id = models.IntegerField(verbose_name='ID значения характеристики')
    # order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    # created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    class Meta:
        verbose_name = 'Характеристика ребенка'
        verbose_name_plural = 'Характеристики детей'
        # ordering = ['person_id']
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['person_id', 'characteristic_value_id'],
        #         name='unique_person_characteristic'
        #     )
        # ]
    
    def __str__(self):
        try:
            person = Person.objects.get(id=self.person_id)
            char_value = CharacteristicValue.objects.get(id=self.characteristic_value_id)
            return f"{person.name} - {char_value}"
        except (Person.DoesNotExist, CharacteristicValue.DoesNotExist):
            return f"Связь №{self.id}"