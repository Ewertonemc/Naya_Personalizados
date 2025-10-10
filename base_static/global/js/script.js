function previewImages(input, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (input.files) {
        Array.from(input.files).forEach((file, index) => {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const preview = document.createElement('div');
                preview.className = 'col-md-3 mb-3';
                
                if (file.type.startsWith('image/')) {
                    preview.innerHTML = `
                        <div class="card">
                            <img src="${e.target.result}" class="card-img-top" style="height: 150px; object-fit: cover;">
                            <div class="card-body p-2">
                                <small class="text-muted">${file.name}</small>
                            </div>
                        </div>
                    `;
                } else {
                    preview.innerHTML = `
                        <div class="card">
                            <div class="card-body text-center">
                                <i class="bi bi-file-earmark display-4 text-muted"></i>
                                <small class="d-block text-muted">${file.name}</small>
                            </div>
                        </div>
                    `;
                }
                
                container.appendChild(preview);
            };
            
            reader.readAsDataURL(file);
        });
    }
}

// Função para validar datas
function validarDatas() {
    const dataMaxima = document.querySelector('input[type="date"][name*="data_maxima"]');
    const dataPrevista = document.querySelector('input[type="date"][name*="data_prevista"]');
    
    if (dataMaxima) {
        const hoje = new Date().toISOString().split('T')[0];
        dataMaxima.min = hoje;
    }
    
    if (dataPrevista && dataMaxima) {
        dataPrevista.min = dataMaxima.value || hoje;
    }
}

// Função para calcular totais em tempo real
function setupCalculadora() {
    const precoInputs = document.querySelectorAll('.preco-input');
    const freteInput = document.querySelector('input[name*="valor_frete"]');
    
    function calcular() {
        let subtotal = 0;
        
        precoInputs.forEach(input => {
            const preco = parseFloat(input.value) || 0;
            const quantidade = parseInt(input.dataset.quantidade) || 1;
            const total = preco * quantidade;
            
            // Atualizar campo total do item
            const itemId = input.name.match(/item_(\d+)_preco/);
            if (itemId) {
                const totalField = document.getElementById(`total_${itemId[1]}`);
                if (totalField) {
                    totalField.value = `R$ ${total.toFixed(2)}`;
                }
            }
            
            subtotal += total;
        });
        
        const frete = parseFloat(freteInput?.value) || 0;
        const total = subtotal + frete;
        
        // Atualizar displays
        const subtotalDisplay = document.getElementById('subtotal-itens');
        const freteDisplay = document.getElementById('valor-frete');
        const totalDisplay = document.getElementById('total-geral');
        
        if (subtotalDisplay) subtotalDisplay.textContent = subtotal.toFixed(2).replace('.', ',');
        if (freteDisplay) freteDisplay.textContent = frete.toFixed(2).replace('.', ',');
        if (totalDisplay) totalDisplay.textContent = total.toFixed(2).replace('.', ',');
    }
    
    precoInputs.forEach(input => input.addEventListener('input', calcular));
    if (freteInput) freteInput.addEventListener('input', calcular);
    
    // Calcular inicialmente
    calcular();
}

// Função para animação dos cards de status
function animateStatusCards() {
    const cards = document.querySelectorAll('.status-card');
    
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate__animated', 'animate__fadeInUp');
    });
}

// Função para confirmação de ações importantes
function setupConfirmations() {
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    const rejectButtons = document.querySelectorAll('[data-action="reject"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja remover este item?')) {
                e.preventDefault();
            }
        });
    });
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja rejeitar este orçamento?')) {
                e.preventDefault();
            }
        });
    });
}

// Função para auto-save de rascunhos
function setupAutoSave() {
    const form = document.querySelector('#orcamento-form, #resposta-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const saveKey = `autosave_${window.location.pathname}`;
    
    // Salvar a cada 30 segundos
    setInterval(() => {
        const currentData = new FormData(form);
        localStorage.setItem(saveKey, JSON.stringify(Array.from(currentData.entries())));
    }, 30000);
    
    // Carregar dados salvos ao carregar a página
    const savedData = localStorage.getItem(saveKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            data.forEach(([name, value]) => {
                const field = form.querySelector(`[name="${name}"]`);
                if (field && field.type !== 'file') {
                    field.value = value;
                }
            });
        } catch (e) {
            console.error('Erro ao carregar dados salvos:', e);
        }
    }
    
    // Limpar dados salvos ao enviar formulário
    form.addEventListener('submit', () => {
        localStorage.removeItem(saveKey);
    });
}

// Inicializar todas as funcionalidades
document.addEventListener('DOMContentLoaded', function() {
    validarDatas();
    setupCalculadora();
    animateStatusCards();
    setupConfirmations();
    setupAutoSave();
    
    // Setup de tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});