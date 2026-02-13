document.addEventListener('DOMContentLoaded', function() {
    // Функция для скрытия/показа дочерних элементов
    function toggleTreeBranch(toggleElement) {
        const row = toggleElement.closest('tr');
        const pageId = toggleElement.getAttribute('data-page-id');
        const isCollapsed = toggleElement.textContent === '▶';
        
        // Находим уровень текущего элемента
        const currentLevel = getElementLevel(row);
        
        // Перебираем следующие строки
        let nextRow = row.nextElementSibling;
        
        while (nextRow) {
            const nextLevel = getElementLevel(nextRow);
            
            // Если следующий элемент того же или меньшего уровня - выходим
            if (nextLevel <= currentLevel) {
                break;
            }
            
            // Скрываем или показываем дочерние элементы
            if (isCollapsed) {
                nextRow.style.display = '';
                // Также показываем их тогглы как свернутые
                const childToggle = nextRow.querySelector('.tree-toggle');
                if (childToggle && childToggle.textContent === '▼') {
                    childToggle.textContent = '▶';
                }
            } else {
                nextRow.style.display = 'none';
            }
            
            nextRow = nextRow.nextElementSibling;
        }
        
        // Меняем иконку тоггла
        toggleElement.textContent = isCollapsed ? '▼' : '▶';
        
        // Сохраняем состояние в localStorage
        saveTreeState(pageId, isCollapsed);
    }
    
    // Функция для определения уровня элемента по отступам
    function getElementLevel(row) {
        const titleCell = row.querySelector('th, td');
        if (!titleCell) return 0;
        
        const content = titleCell.innerHTML;
        const indentMatch = content.match(/&nbsp;&nbsp;&nbsp;&nbsp;/g);
        return indentMatch ? indentMatch.length : 0;
    }
    
    // Функция для сохранения состояния дерева
    function saveTreeState(pageId, isCollapsed) {
        const state = JSON.parse(localStorage.getItem('pages_tree_state') || '{}');
        state[pageId] = isCollapsed; // true = развернут, false = свернут
        localStorage.setItem('pages_tree_state', JSON.stringify(state));
    }
    
    // Функция для загрузки состояния дерева
    function loadTreeState() {
        return JSON.parse(localStorage.getItem('pages_tree_state') || '{}');
    }
    
    // Функция для инициализации дерева (все элементы свернуты)
    function initializeTree() {
        const state = {};
        const allRows = document.querySelectorAll('#result_list tbody tr');
        
        allRows.forEach((row, index) => {
            if (index === 0) return; // Пропускаем заголовок
            
            const toggle = row.querySelector('.tree-toggle');
            if (toggle) {
                const pageId = toggle.getAttribute('data-page-id');
                state[pageId] = false; // По умолчанию все свернуто
                
                // Скрываем дочерние элементы
                const currentLevel = getElementLevel(row);
                let nextRow = row.nextElementSibling;
                
                while (nextRow) {
                    const nextLevel = getElementLevel(nextRow);
                    if (nextLevel <= currentLevel) break;
                    
                    nextRow.style.display = 'none';
                    nextRow = nextRow.nextElementSibling;
                }
            }
        });
        
        localStorage.setItem('pages_tree_state', JSON.stringify(state));
    }
    
    // Обработчик кликов по тогглам
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tree-toggle')) {
            e.preventDefault();
            e.stopPropagation();
            toggleTreeBranch(e.target);
        }
    });
    
    // Инициализация при загрузке
    const treeState = loadTreeState();
    const isFirstLoad = Object.keys(treeState).length === 0;
    
    if (isFirstLoad) {
        // Первая загрузка - сворачиваем все
        initializeTree();
    } else {
        // Восстанавливаем сохраненное состояние
        const allRows = document.querySelectorAll('#result_list tbody tr');
        
        allRows.forEach((row, index) => {
            if (index === 0) return;
            
            const toggle = row.querySelector('.tree-toggle');
            if (toggle) {
                const pageId = toggle.getAttribute('data-page-id');
                const shouldBeExpanded = treeState[pageId];
                
                if (shouldBeExpanded) {
                    toggle.textContent = '▼';
                    // Показываем дочерние элементы
                    const currentLevel = getElementLevel(row);
                    let nextRow = row.nextElementSibling;
                    
                    while (nextRow) {
                        const nextLevel = getElementLevel(nextRow);
                        if (nextLevel <= currentLevel) break;
                        
                        nextRow.style.display = '';
                        nextRow = nextRow.nextElementSibling;
                    }
                } else {
                    toggle.textContent = '▶';
                }
            }
        });
    }
    
    // кнопка для свертывания/развертывания дерева
    const toolbar = document.querySelector('#changelist .paginator');
    if (toolbar) {
        const collapseAllBtn = document.createElement('button');
        collapseAllBtn.type = 'button';
        collapseAllBtn.className = 'button';
        collapseAllBtn.textContent = 'Свернуть все';
        collapseAllBtn.style.marginRight = '10px';
        
        const expandAllBtn = document.createElement('button');
        expandAllBtn.type = 'button';
        expandAllBtn.className = 'button';
        expandAllBtn.textContent = 'Развернуть все';
        
        collapseAllBtn.addEventListener('click', function() {
            const toggles = document.querySelectorAll('.tree-toggle');
            toggles.forEach(toggle => {
                if (toggle.textContent === '▼') {
                    toggleTreeBranch(toggle);
                }
            });
        });
        
        expandAllBtn.addEventListener('click', function() {
            const toggles = document.querySelectorAll('.tree-toggle');
            toggles.forEach(toggle => {
                if (toggle.textContent === '▶') {
                    toggleTreeBranch(toggle);
                }
            });
        });
        
        toolbar.parentNode.insertBefore(expandAllBtn, toolbar);
        toolbar.parentNode.insertBefore(collapseAllBtn, toolbar);
    }
});