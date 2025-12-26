(function() {
    'use strict';
    
    // Define species-specific vaccines
    const VACCINE_LISTS = {
        'dog': ['rabies', 'dhppi', 'leptospirosis', 'parvovirus', 'parainfluenza', 'other'],
        'cat': ['rabies', 'dappi', 'other'],
        'other': ['rabies', 'other']
    };
    
    function filterVaccineChoices() {
        const speciesSelect = document.getElementById('id_species');
        if (!speciesSelect) return;
        
        const species = speciesSelect.value || 'other';
        const allowedVaccines = VACCINE_LISTS[species] || VACCINE_LISTS['other'];
        
        console.log('Filtering vaccines for species:', species, 'Allowed:', allowedVaccines);
        
        // Filter all vaccine dropdowns
        const vaccineSelects = document.querySelectorAll('[id^="id_vaccinations-"][id$="-vaccine_name"]');
        vaccineSelects.forEach(function(select) {
            if (select.disabled) return; // Skip readonly fields
            
            Array.from(select.options).forEach(function(option) {
                if (option.value === '') {
                    option.style.display = ''; // Always show "-------"
                } else if (allowedVaccines.includes(option.value)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    }
    
    // Run immediately on script load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', filterVaccineChoices);
    } else {
        filterVaccineChoices();
    }
    
    // Also run after a short delay to catch late-loaded inlines
    setTimeout(filterVaccineChoices, 500);
    setTimeout(filterVaccineChoices, 1000);
    
    // Listen for species changes
    setTimeout(function() {
        const speciesSelect = document.getElementById('id_species');
        if (speciesSelect) {
            speciesSelect.addEventListener('change', function() {
                console.log('Species changed to:', this.value);
                filterVaccineChoices();
            });
        }
    }, 100);
    
    // Listen for new inline forms being added
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            console.log('New vaccination form added');
            setTimeout(filterVaccineChoices, 100);
        });
    }
    
})();