(function($) {
    $(document).ready(function() {
        // Function to filter vaccine choices based on species
        function filterVaccines() {
            const animalId = $('#id_animal').val();
            
            if (!animalId) return;
            
            // Get animal species via AJAX
            $.get('/api/v1/animals/' + animalId + '/', function(data) {
                const species = data.species;
                const vaccineSelect = $('#id_vaccine_name');
                const allOptions = vaccineSelect.find('option');
                
                // Define species-specific vaccines
                const dogVaccines = ['rabies', 'distemper', 'parvovirus', 'hepatitis', 
                                    'leptospirosis', 'parainfluenza', 'coronavirus', 'bordetella'];
                const catVaccines = ['rabies', 'feline_leukemia', 'feline_distemper', 
                                    'calicivirus', 'rhinotracheitis', 'chlamydia', 'fip'];
                
                // Filter options
                allOptions.each(function() {
                    const value = $(this).val();
                    if (!value || value === 'other') {
                        $(this).show(); // Always show empty and "other"
                    } else if (species === 'Σκύλος' && dogVaccines.includes(value)) {
                        $(this).show();
                    } else if (species === 'Γάτα' && catVaccines.includes(value)) {
                        $(this).show();
                    } else if (species === 'Άλλο') {
                        $(this).show(); // Show all for "other" species
                    } else {
                        $(this).hide();
                    }
                });
            });
        }
        
        // Apply filtering on load and when animal selection changes
        $('#id_animal').change(filterVaccines);
        filterVaccines();
    });
})(django.jQuery);