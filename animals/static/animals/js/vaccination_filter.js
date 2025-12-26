(function($) {
    'use strict';
    
    // Define species-specific vaccines
    const VACCINE_LISTS = {
        'dog': ['rabies', 'dhppi', 'leptospirosis', 'parvovirus', 'parainfluenza', 'other'],
        'cat': ['rabies', 'dappi', 'other'],
        'other': ['rabies', 'other']
    };
    
    function filterVaccineChoices() {
        // Get the animal's species from the form
        const speciesSelect = document.getElementById('id_species');
        if (!speciesSelect) return;
        
        const species = speciesSelect.value;
        
        // Filter all vaccine dropdowns
        document.querySelectorAll('[id^="id_vaccinations-"][id$="-vaccine_name"]').forEach(function(select) {
            if (select.disabled) return; // Skip readonly fields
            
            const currentValue = select.value;
            const allowedVaccines = VACCINE_LISTS[species] || VACCINE_LISTS['other'];
            
            // Show/hide options based on species
            Array.from(select.options).forEach(function(option) {
                if (option.value === '') {
                    option.style.display = ''; // Always show "-------"
                } else if (allowedVaccines.includes(option.value)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
            
            // Reset if current value is not allowed
            if (currentValue && !allowedVaccines.includes(currentValue)) {
                select.value = '';
            }
        });
    }
    
    // Run on page load
    $(document).ready(function() {
        filterVaccineChoices();
        
        // Re-filter when species changes
        const speciesSelect = document.getElementById('id_species');
        if (speciesSelect) {
            speciesSelect.addEventListener('change', filterVaccineChoices);
        }
        
        // Re-filter when new vaccination inline is added
        $(document).on('formset:added', function() {
            filterVaccineChoices();
        });
    });
    
})(django.jQuery);