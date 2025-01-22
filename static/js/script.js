document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function getFilters() {
        const filters = {};
        
        // Get similarity metric
        filters.similarity_metric = document.getElementById('similarity-metric').value;

        // Get numeric range filters
        const numericFields = ['price', 'review_scores_rating', 'accommodates', 'bedrooms', 'beds'];
        numericFields.forEach(field => {
            const minVal = document.getElementById(`${field}-min`).value;
            const maxVal = document.getElementById(`${field}-max`).value;
            if (minVal || maxVal) {
                filters[`${field}_range`] = [
                    minVal ? parseFloat(minVal) : null,
                    maxVal ? parseFloat(maxVal) : null
                ];
            }
        });

        // Get categorical filters
        ['host_response_time', 'neighbourhood_cleansed', 'property_type', 'room_type'].forEach(field => {
            const value = document.getElementById(field).value;
            if (value) {
                filters[field] = value;
            }
        });

        // Get selected amenities
        const selectedAmenities = Array.from(document.querySelectorAll('.amenity-checkbox:checked'))
            .map(checkbox => checkbox.value);
        if (selectedAmenities.length > 0) {
            filters.amenities = selectedAmenities;
        }

        return filters;
    }

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }

        const filters = getFilters();
        
        // Show loading state
        resultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

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
        .then(response => response.json())
        .then(results => {
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
            <div class="col-md-6 col-lg-4">
                <div class="card listing-card">
                    <img src="${listing.picture_url || 'https://via.placeholder.com/300x200?text=No+Image'}" 
                         class="card-img-top listing-image" 
                         alt="${listing.name}">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="${listing.listing_url}" target="_blank" class="text-decoration-none">
                                ${listing.name}
                            </a>
                        </h5>
                        <p class="card-text description-text">
                            ${listing.description ? listing.description.substring(0, 150) + '...' : 'No description available'}
                        </p>
                        <p class="card-text">
                            <span class="price">€${listing.price}/night</span><br>
                            <span class="rating">★ ${listing.review_scores_rating || 'N/A'}</span>
                        </p>
                        <p class="card-text">
                            <small class="text-muted">
                                ${listing.property_type} · ${listing.room_type}<br>
                                ${listing.accommodates} guests · ${listing.bedrooms || '?'} bedrooms · ${listing.beds || '?'} beds
                            </small>
                        </p>
                        <p class="card-text">
                            <small class="text-muted">
                                ${listing.neighbourhood}<br>
                                Response time: ${listing.host_response_time || 'N/A'}
                            </small>
                        </p>
                        <div class="amenities">
                            ${listing.amenities.slice(0, 5).map(amenity => 
                                `<span class="badge bg-secondary amenity-badge">${amenity}</span>`
                            ).join('')}
                            ${listing.amenities.length > 5 ? 
                                `<span class="badge bg-secondary amenity-badge">+${listing.amenities.length - 5} more</span>` : 
                                ''}
                        </div>
                        <p class="card-text mt-2">
                            <small class="text-muted">Similarity: ${(listing.similarity_score * 100).toFixed(1)}%</small>
                        </p>
                    </div>
                </div>
            </div>
        `).join('');
    }
});
