// ===== INTERNATIONALIZATION (i18n) =====

let currentLanguage = localStorage.getItem('language') || 'tr';
let translations = {};

// Load translation files
async function loadTranslations() {
    try {
        const response = await fetch(`./${currentLanguage}.json?v=` + Date.now());
        if (response.ok) {
            translations = await response.json();
            applyTranslations();
        }
    } catch (error) {
        console.warn('Çeviriler yüklenemedi:', error);
    }
}

// Apply translations to elements with data-i18n attribute
function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = getNestedTranslation(key);
        if (translation) {
            element.textContent = translation;
        }
    });

    // Apply placeholder translations
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        const translation = getNestedTranslation(key);
        if (translation) {
            element.placeholder = translation;
        }
    });
}

// Get nested translation (e.g., "header.title" -> translations.header.title)
function getNestedTranslation(key) {
    const keys = key.split('.');
    let value = translations;
    
    for (let k of keys) {
        if (value && typeof value === 'object' && k in value) {
            value = value[k];
        } else {
            return null;
        }
    }
    
    return typeof value === 'string' ? value : null;
}

// Switch language
function switchLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    
    // Update language buttons opacity
    document.querySelectorAll('[id^="langBtn-"]').forEach(btn => {
        btn.style.opacity = btn.id === `langBtn-${lang}` ? '1' : '0.5';
    });
    
    loadTranslations();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set initial language button opacity
    const langBtn = document.getElementById(`langBtn-${currentLanguage}`);
    if (langBtn) langBtn.style.opacity = '1';
    
    loadTranslations();
});
