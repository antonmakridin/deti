from django.contrib import admin
from .models import Characteristic, CharacteristicValue, Person, PersonCharacteristic

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'get_values_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'description', 'order', 'is_active']
    change_list_template = 'admin/catalog/characteristic/change_list.html'
    
    def get_values_count(self, obj):
        return CharacteristicValue.objects.filter(characteristic_id=obj.id).count()
    get_values_count.short_description = 'Кол-во значений'

@admin.register(CharacteristicValue)
class CharacteristicValueAdmin(admin.ModelAdmin):
    list_display = ['get_characteristic_display', 'value', 'characteristic_id']
    list_filter = ['characteristic_id']
    search_fields = ['value']
    fields = ['characteristic_id', 'value']
    
    def get_characteristic_display(self, obj):
        try:
            char = Characteristic.objects.get(id=obj.characteristic_id)
            return f"{char.name}"
        except Characteristic.DoesNotExist:
            return f"Характеристика #{obj.characteristic_id}"
    get_characteristic_display.short_description = 'Характеристика'
    get_characteristic_display.allow_tags = True

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_age', 'is_published', 'created_at', 'get_siblings_count']
    list_filter = ['is_published', 'created_at']
    list_editable = ['is_published']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'photo', 'birth_date', 'description')
        }),
        ('Характеристики', {
            'fields': ('characteristics_ids',),
            'description': 'Список ID значений характеристик в формате JSON, например: [1, 2, 3]'
        }),
        ('Братья/сестры', {
            'fields': ('siblings_ids',),
            'description': 'Список ID братьев/сестер в формате JSON, например: [1, 2, 3]'
        }),
        ('Дополнительно', {
            'fields': ('photo_publish_date', 'is_published')
        }),
    )
    change_list_template = 'admin/catalog/person/change_list.html'
    
    def get_age(self, obj):
        age = obj.get_age()
        return f"{age} лет" if age else "-"
    get_age.short_description = 'Возраст'
    
    def get_siblings_count(self, obj):
        return len(obj.siblings_ids) if obj.siblings_ids else 0
    get_siblings_count.short_description = 'Братьев/сестер'

@admin.register(PersonCharacteristic)
class PersonCharacteristicAdmin(admin.ModelAdmin):
    list_display = ['get_person_display', 'get_characteristic_value_display']
    list_filter = ['characteristic_value_id']
    search_fields = ['person_id', 'characteristic_value_id']
    fields = ['person_id', 'characteristic_value_id']
    
    def get_person_display(self, obj):
        try:
            person = Person.objects.get(id=obj.person_id)
            return f"{person.name} <span class='char-id'>#{obj.person_id}</span>"
        except Person.DoesNotExist:
            return f"Ребонок #{obj.person_id}"
    get_person_display.short_description = 'Ребенок'
    get_person_display.allow_tags = True
    
    def get_characteristic_value_display(self, obj):
        try:
            char_value = CharacteristicValue.objects.get(id=obj.characteristic_value_id)
            return str(char_value)
        except CharacteristicValue.DoesNotExist:
            return f"Значение #{obj.characteristic_value_id}"
    get_characteristic_value_display.short_description = 'Значение характеристики'