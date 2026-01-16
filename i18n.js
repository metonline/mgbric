// ===== MULTILINGUAL SYSTEM (I18N) =====
let currentLanguage = localStorage.getItem('language') || 'tr';
let translations = {};

// Load translations
async function loadTranslations(lang) {
    try {
        const response = await fetch(`${lang}.json`);
        translations[lang] = await response.json();
    } catch (e) {
        console.error(`Failed to load ${lang}.json:`, e);
    }
}

// Initialize language
async function initLanguage() {
    await loadTranslations('tr');
    await loadTranslations('en');
    switchLanguage(currentLanguage);
}

// Switch language
function switchLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Language ${lang} not loaded`);
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const keys = element.getAttribute('data-i18n').split('.');
        let value = translations[lang];
        
        for (let key of keys) {
            value = value[key];
            if (!value) break;
        }
        
        if (value) {
            element.textContent = value;
        }
    });
    
    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const keys = element.getAttribute('data-i18n-placeholder').split('.');
        let value = translations[lang];
        
        for (let key of keys) {
            value = value[key];
            if (!value) break;
        }
        
        if (value) {
            element.placeholder = value;
        }
    });
    
    // Update language button styles (for header buttons)
    if (document.getElementById('langTR')) {
        document.getElementById('langTR').style.opacity = lang === 'tr' ? '1' : '0.5';
    }
    if (document.getElementById('langEN')) {
        document.getElementById('langEN').style.opacity = lang === 'en' ? '1' : '0.5';
    }
    
    // Update language button styles (for flag images)
    if (document.getElementById('langBtn-tr')) {
        document.getElementById('langBtn-tr').style.opacity = lang === 'tr' ? '1' : '0.5';
    }
    if (document.getElementById('langBtn-en')) {
        document.getElementById('langBtn-en').style.opacity = lang === 'en' ? '1' : '0.5';
    }
    
    // Update title
    if (translations[lang].title) {
        document.title = translations[lang].title;
    }
    
    // Trigger modal re-render if it's open
    if (typeof showPlayerTab !== 'undefined' && window.currentPlayerTab) {
        showPlayerTab(window.currentPlayerTab);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initLanguage);

// Helper function to get translation value
function getTranslation(keyPath) {
    const keys = keyPath.split('.');
    let value = translations[currentLanguage];
    
    for (let key of keys) {
        value = value[key];
        if (!value) return keyPath;
    }
    
    return value || keyPath;
}

// Shorthand alias for translate
const i18n = {
    translate: function(keyPath) {
        return getTranslation(keyPath);
    },
    getTranslation: getTranslation,
    get currentLang() {
        return currentLanguage;
    }
};
