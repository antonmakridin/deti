from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Person, Characteristic, CharacteristicValue

def person_list(request):
    # Получаем ВСЕ активные характеристики для фильтров
    characteristics = Characteristic.objects.filter(is_active=True).order_by('order')
    
    # Получаем ID всех активных характеристик
    filter_characteristic_ids = list(characteristics.values_list('id', flat=True))
    
    # Получаем все значения характеристик для фильтруемых характеристик
    characteristic_values = CharacteristicValue.objects.filter(
        characteristic_id__in=filter_characteristic_ids
    ).order_by('characteristic_id', 'value')
    
    # Создаем словарь значений по ID характеристики
    values_by_char = {}
    for char_value in characteristic_values:
        char_id = char_value.characteristic_id
        if char_id not in values_by_char:
            values_by_char[char_id] = []
        values_by_char[char_id].append(char_value)
    
    # Базовый запрос
    persons = Person.objects.filter(is_published=True)
    
    # Применяем фильтры для каждой характеристики отдельно
    for characteristic in characteristics:
        param_name = f"char_{characteristic.id}"
        selected_values = request.GET.getlist(param_name)
        
        if selected_values:
            # Преобразуем строки в числа
            selected_int_values = [int(val) for val in selected_values if val and val.isdigit()]
            
            if selected_int_values:
                
                # Создаем список условий для каждого значения
                filter_conditions = Q()
                for value_id in selected_int_values:
                    filter_conditions |= Q(characteristics_ids__contains=[value_id])
                
                # Применяем фильтр
                persons = persons.filter(filter_conditions)
    
    # Фильтрация по возрасту
    min_age = request.GET.get('min_age', '')
    max_age = request.GET.get('max_age', '')
    
    if min_age or max_age:
        min_age_int = int(min_age) if min_age else None
        max_age_int = int(max_age) if max_age else None
        
        # Создаем список ID людей, которые подходят по возрасту
        age_filtered_ids = []
        for person in persons:
            age = person.get_age()
            if age is not None:
                include_person = True
                if min_age_int is not None and age < min_age_int:
                    include_person = False
                if max_age_int is not None and age > max_age_int:
                    include_person = False
                
                if include_person:
                    age_filtered_ids.append(person.id)
        
        # Применяем фильтр
        persons = persons.filter(id__in=age_filtered_ids)
    
    # Убираем дубликаты
    persons = persons.distinct()
    
    # Пагинация
    paginator = Paginator(persons, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Фильтруем данные
    filter_data = {}
    for characteristic in characteristics:
        values = values_by_char.get(characteristic.id, [])
        selected_values = request.GET.getlist(f"char_{characteristic.id}")
        filter_data[characteristic.id] = {
            'characteristic': characteristic,
            'values': values,
            'selected': selected_values
        }
    
    context = {
        'page_obj': page_obj,
        'filter_data': filter_data,
        'current_filters': request.GET,
        'min_age': min_age,
        'max_age': max_age,
    }
    return render(request, 'catalog/person_list.html', context)

def person_detail(request, pk):
    person = get_object_or_404(Person, pk=pk, is_published=True)
    characteristics = person.get_characteristics_dict()
    
    context = {
        'person': person,
        'characteristics': characteristics,
    }
    return render(request, 'catalog/person_detail.html', context)