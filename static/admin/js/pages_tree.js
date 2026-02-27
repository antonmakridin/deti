// Немедленно выполняющаяся функция для начального сворачивания
(function() {
    // Функция для определения уровня по отступам
    function getLevelFromRow(row) {
        const titleCell = row.querySelector('th.field-title_with_toggle');
        if (!titleCell) return 0;
        const content = titleCell.innerHTML;
        const indentMatch = content.match(/&nbsp;&nbsp;&nbsp;&nbsp;/g);
        return indentMatch ? indentMatch.length : 0;
    }
    
    // Функция для проверки, есть ли видимые дочерние элементы
    function hasVisibleChildren(row) {
        const level = getLevelFromRow(row);
        let nextRow = row.nextElementSibling;
        
        while (nextRow) {
            const nextLevel = getLevelFromRow(nextRow);
            if (nextLevel <= level) break;
            
            // Если нашли хотя бы один видимый дочерний элемент
            if (nextRow.style.display !== 'none') {
                return true;
            }
            nextRow = nextRow.nextElementSibling;
        }
        return false;
    }
    
    // Функция для сворачивания всех дочерних элементов
    function collapseAllChildren() {
        const savedState = JSON.parse(localStorage.getItem('pages_tree_state') || '{}');
        const rows = document.querySelectorAll('#result_list tbody tr');
        if (rows.length === 0) {
            setTimeout(collapseAllChildren, 50);
            return;
        }
        
        // Сначала скрываем все дочерние элементы
        rows.forEach((row, index) => {
            if (index === 0) return; // Пропускаем заголовок
            
            const level = getLevelFromRow(row);
            
            // Если это не корневой элемент (есть отступы) - скрываем
            if (level > 0) {
                row.style.display = 'none';
            }
            
            // Находим или создаем тоггл
            const titleCell = row.querySelector('th.field-title_with_toggle');
            let toggle = titleCell.querySelector('.tree-toggle');
            
            if (!toggle) {
                toggle = document.createElement('span');
                toggle.className = 'tree-toggle';
                toggle.style.cssText = 'cursor: pointer; margin-right: 5px; display: inline-block; width: 16px;';
                
                // Ищем ID страницы из ссылки
                const pageLink = row.querySelector('a');
                if (pageLink) {
                    const href = pageLink.getAttribute('href');
                    const match = href.match(/\/admin\/page\/page\/(\d+)\//);
                    if (match) {
                        const pageId = match[1];
                        toggle.setAttribute('data-page-id', pageId);
                        
                        // Вставляем тоггл в начало ячейки
                        const firstChild = titleCell.firstChild;
                        if (firstChild && firstChild.nodeType === 3) {
                            const text = firstChild.textContent;
                            firstChild.textContent = '';
                            titleCell.insertBefore(toggle, firstChild);
                            titleCell.appendChild(document.createTextNode(text));
                        } else {
                            titleCell.insertBefore(toggle, firstChild);
                        }
                    }
                }
            }
        });
        
        // Разворачиваем сохраненные элементы
        rows.forEach(row => {
            const toggle = row.querySelector('.tree-toggle');
            if (!toggle) return;
            
            const pageId = toggle.getAttribute('data-page-id');
            if (savedState[pageId] === true) {
                const level = getLevelFromRow(row);
                let nextRow = row.nextElementSibling;
                
                while (nextRow) {
                    const nextLevel = getLevelFromRow(nextRow);
                    if (nextLevel <= level) break;
                    nextRow.style.display = '';
                    nextRow = nextRow.nextElementSibling;
                }
            }
        });
        
        // Теперь устанавливаем иконки на основе фактической видимости дочерних элементов
        rows.forEach(row => {
            const toggle = row.querySelector('.tree-toggle');
            if (!toggle) return;
            
            const hasChildren = hasVisibleChildren(row);
            if (hasChildren) {
                toggle.textContent = '▼'; // Развернут
            } else {
                toggle.textContent = '▶'; // Свернут
            }
        });
    }
    
    // Запускаем сворачивание
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', collapseAllChildren);
    } else {
        collapseAllChildren();
    }
    window.addEventListener('load', collapseAllChildren);
})();

// Основной код для интерактивности
document.addEventListener('DOMContentLoaded', function() {
    // Функция для определения уровня элемента
    function getElementLevel(row) {
        const titleCell = row.querySelector('th.field-title_with_toggle');
        if (!titleCell) return 0;
        const content = titleCell.innerHTML;
        const indentMatch = content.match(/&nbsp;&nbsp;&nbsp;&nbsp;/g);
        return indentMatch ? indentMatch.length : 0;
    }
    
    // Функция для получения дочерних элементов
    function getChildRows(row) {
        const currentLevel = getElementLevel(row);
        const children = [];
        let nextRow = row.nextElementSibling;
        
        while (nextRow) {
            const nextLevel = getElementLevel(nextRow);
            if (nextLevel <= currentLevel) break;
            children.push(nextRow);
            nextRow = nextRow.nextElementSibling;
        }
        
        return children;
    }
    
    // Функция для проверки видимости дочерних элементов
    function hasVisibleChildren(row) {
        const children = getChildRows(row);
        return children.some(child => child.style.display !== 'none');
    }
    
    // Функция для обновления иконки на основе видимости
    function updateToggleIcon(toggle) {
        const row = toggle.closest('tr');
        const hasVisible = hasVisibleChildren(row);
        toggle.textContent = hasVisible ? '▼' : '▶';
    }
    
    // Функция для сворачивания/разворачивания
    function toggleTreeBranch(toggleElement) {
        const row = toggleElement.closest('tr');
        const pageId = toggleElement.getAttribute('data-page-id');
        const isExpanded = toggleElement.textContent === '▼';
        
        const childRows = getChildRows(row);
        
        childRows.forEach(childRow => {
            childRow.style.display = isExpanded ? 'none' : '';
            
            // Обновляем иконки дочерних элементов
            const childToggle = childRow.querySelector('.tree-toggle');
            if (childToggle) {
                updateToggleIcon(childToggle);
            }
        });
        
        // Обновляем иконку текущего элемента
        updateToggleIcon(toggleElement);
        
        // Сохраняем состояние
        const state = JSON.parse(localStorage.getItem('pages_tree_state') || '{}');
        state[pageId] = !isExpanded;
        localStorage.setItem('pages_tree_state', JSON.stringify(state));
    }
    
    // Функции для кнопок
    function collapseAll() {
        const toggles = document.querySelectorAll('.tree-toggle');
        toggles.forEach(toggle => {
            const row = toggle.closest('tr');
            const childRows = getChildRows(row);
            if (childRows.length > 0 && toggle.textContent === '▼') {
                toggleTreeBranch(toggle);
            }
        });
    }
    
    function expandAll() {
        const toggles = document.querySelectorAll('.tree-toggle');
        toggles.forEach(toggle => {
            const row = toggle.closest('tr');
            const childRows = getChildRows(row);
            if (childRows.length > 0 && toggle.textContent === '▶') {
                toggleTreeBranch(toggle);
            }
        });
    }
    
    // Обработчик кликов
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tree-toggle')) {
            e.preventDefault();
            e.stopPropagation();
            toggleTreeBranch(e.target);
        }
    });
    
    // Добавляем кнопки управления
    function addControlButtons() {
        const toolbar = document.querySelector('#changelist .paginator');
        if (!toolbar) return;
        
        if (document.querySelector('.tree-control-buttons')) return;
        
        const container = document.createElement('div');
        container.className = 'tree-control-buttons';
        container.style.cssText = 'margin: 10px 0; padding: 10px; background: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; display: flex; gap: 10px;';
        
        const collapseBtn = document.createElement('button');
        collapseBtn.type = 'button';
        collapseBtn.className = 'button';
        collapseBtn.textContent = 'Свернуть все';
        collapseBtn.addEventListener('click', collapseAll);
        
        const expandBtn = document.createElement('button');
        expandBtn.type = 'button';
        expandBtn.className = 'button';
        expandBtn.textContent = 'Развернуть все';
        expandBtn.addEventListener('click', expandAll);
        
        const resetBtn = document.createElement('button');
        resetBtn.type = 'button';
        resetBtn.className = 'button';
        resetBtn.textContent = 'Сбросить';
        resetBtn.style.cssText = 'background-color: #dc3545; color: white; border-color: #dc3545;';
        resetBtn.addEventListener('click', () => {
            if (confirm('Сбросить состояние?')) {
                localStorage.removeItem('pages_tree_state');
                location.reload();
            }
        });
        
        container.appendChild(collapseBtn);
        container.appendChild(expandBtn);
        container.appendChild(resetBtn);
        toolbar.parentNode.insertBefore(container, toolbar);
    }
    
    addControlButtons();
});