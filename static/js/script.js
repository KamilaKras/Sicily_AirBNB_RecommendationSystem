document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');

    console.log('Elements found:', {
        searchInput: !!searchInput,
        searchButton: !!searchButton,
        resultsContainer: !!resultsContainer
    });

    searchButton.addEventListener('click', function() {
        console.log('Search button clicked');
        performSearch();
    });
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            console.log('Enter key pressed');
            performSearch();
        }
    });

    function getFilters() {
        const filters = {};
        
        // Get similarity metric
        const similarityMetric = document.getElementById('similarity-metric');
        if (similarityMetric) {
            filters.similarity_metric = similarityMetric.value;
        }

        // Get numeric range filters
        const numericFields = ['price', 'review_scores_rating', 'accommodates', 'bedrooms', 'beds'];
        numericFields.forEach(field => {
            const minElement = document.getElementById(`${field}-min`);
            const maxElement = document.getElementById(`${field}-max`);
            if (minElement || maxElement) {
                const minVal = minElement ? minElement.value : null;
                const maxVal = maxElement ? maxElement.value : null;
                if (minVal || maxVal) {
                    filters[`${field}_range`] = [
                        minVal ? parseFloat(minVal) : null,
                        maxVal ? parseFloat(maxVal) : null
                    ];
                }
            }
        });

        // Get categorical filters - only if they exist
        const categoricalFields = ['host_response_time', 'neighbourhood_cleansed', 'property_type', 'room_type'];
        categoricalFields.forEach(field => {
            const element = document.getElementById(field);
            if (element && element.value) {
                filters[field] = element.value;
            }
        });

        // Get selected amenities - only if they exist
        const amenityCheckboxes = document.querySelectorAll('.amenity-checkbox:checked');
        if (amenityCheckboxes.length > 0) {
            filters.amenities = Array.from(amenityCheckboxes).map(checkbox => checkbox.value);
        }

        return filters;
    }

    function performSearch() {
        console.log('Performing search');
        const query = searchInput.value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }

        const filters = getFilters();
        console.log('Filters:', filters);
        
        // Show loading state
        resultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        console.log('Sending fetch request to /search');
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                filters: filters
            })
        })
        .then(response => {
            console.log('Got response:', response.status);
            return response.json();
        })
        .then(results => {
            console.log('Got results:', results);
            displayResults(results);
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<div class="alert alert-danger">An error occurred while searching. Please try again.</div>';
        });
    }

    function displayResults(results) {
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No results found. Try adjusting your search criteria.</div>';
            return;
        }

        resultsContainer.innerHTML = results.map(listing => `
            <div class="col-sm-6 col-lg-4">
                <div class="card listing-card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="${listing.listing_url}" target="_blank" class="text-decoration-none">
                                ${listing.name}
                            </a>
                        </h5>
                        <p class="card-text description-text">
                            ${listing.description ? listing.description.substring(0, 100) + '...' : 'No description available'}
                        </p>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="price">€${listing.price}/night</span>
                            <span class="rating">★ ${listing.review_scores_rating || 'N/A'}</span>
                        </div>
                        <p class="card-text">
                            <small class="text-muted">
                                ${listing.property_type} · ${listing.room_type}<br>
                                ${listing.accommodates} guests · ${listing.bedrooms || '?'} bed
                            </small>
                        </p>
                        <div class="amenities">
                            ${listing.amenities.slice(0, 3).map(amenity => 
                                `<span class="badge bg-secondary amenity-badge">${amenity}</span>`
                            ).join('')}
                            ${listing.amenities.length > 3 ? 
                                `<span class="badge bg-secondary amenity-badge">+${listing.amenities.length - 3} more</span>` : 
                                ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
});
