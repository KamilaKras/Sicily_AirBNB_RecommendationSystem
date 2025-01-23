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
        const resultsContainer = document.getElementById('results-container');
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        let html = '<div class="results-list">';
        results.forEach((result, index) => {
            const amenitiesHtml = result.amenities.slice(0, 5).map(amenity => 
                `<span class="badge bg-secondary me-1">${amenity}</span>`
            ).join('');

            html += `
                <div class="result-card mb-3">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <h5 class="card-title">${result.name}</h5>
                                <button class="btn btn-link expand-btn" data-result-id="${index}">
                                    <i class="fas fa-chevron-down"></i>
                                </button>
                            </div>
                            <div class="basic-info">
                                <p class="card-text">
                                    <strong>Price:</strong> $${result.price}/night<br>
                                    <strong>Type:</strong> ${result.property_type} - ${result.room_type}<br>
                                    <strong>Location:</strong> ${result.neighbourhood}<br>
                                    <strong>Rating:</strong> ${result.review_scores_rating || 'N/A'}<br>
                                    <strong>Accommodates:</strong> ${result.accommodates} guests
                                </p>
                                <div class="amenities mb-2">
                                    ${amenitiesHtml}
                                </div>
                            </div>
                            <div class="detailed-info collapse" id="details-${index}">
                                <hr>
                                <h6>Description</h6>
                                <p>${result.description}</p>

                                <h6>Neighborhood Overview</h6>
                                <p>${result.neighborhood_overview || 'No neighborhood overview available.'}</p>
                                
                                <div class="additional-details">
                                    <p>
                                        <strong>Bedrooms:</strong> ${result.bedrooms || 'N/A'}<br>
                                        <strong>Beds:</strong> ${result.beds || 'N/A'}<br>
                                        <strong>Bathrooms:</strong> ${result.bathrooms || 'N/A'}<br>
                                        <strong>Minimum Nights:</strong> ${result.minimum_nights}<br>
                                        <strong>Maximum Nights:</strong> ${result.maximum_nights}<br>
                                    </p>
                                </div>
                                
                                <h6>All Amenities</h6>
                                <div class="all-amenities">
                                    ${result.amenities.map(amenity => 
                                        `<span class="badge bg-secondary me-1 mb-1">${amenity}</span>`
                                    ).join('')}
                                </div>

                                <h6 class="mt-4">Host Information</h6>
                                <div class="host-info mb-3">
                                    <div class="host-header d-flex align-items-center mb-2">
                                        <h6 class="mb-0">Hosted by ${result.host_name}</h6>
                                        ${result.host_is_superhost ? '<span class="badge bg-success ms-2">Superhost</span>' : ''}
                                    </div>
                                    <p class="mb-2">
                                        <strong>Host Since:</strong> ${result.host_since || 'Not specified'}<br>
                                        <strong>Location:</strong> ${result.host_location || 'Not specified'}<br>
                                        <strong>Response Time:</strong> ${result.host_response_time || 'Not specified'}<br>
                                        <strong>Response Rate:</strong> ${result.host_response_rate || 'Not specified'}<br>
                                        <strong>Acceptance Rate:</strong> ${result.host_acceptance_rate || 'Not specified'}<br>
                                        <strong>Total Listings:</strong> ${result.host_listings_count || '0'}<br>
                                        <strong>Identity Verified:</strong> ${result.host_identity_verified ? 'Yes' : 'No'}
                                    </p>
                                    ${result.host_about ? `
                                        <div class="host-about">
                                            <strong>About the Host:</strong>
                                            <p class="mb-0">${result.host_about}</p>
                                        </div>
                                    ` : ''}
                                </div>

                                <h6>Reviews</h6>
                                <div class="reviews-info mb-3">
                                    <div class="reviews-header d-flex align-items-center justify-content-between mb-3">
                                        <div>
                                            <h6 class="mb-0">
                                                <i class="fas fa-star text-warning"></i>
                                                ${result.review_scores_rating || 'N/A'} · ${result.number_of_reviews} reviews
                                            </h6>
                                        </div>
                                    </div>
                                    <div class="review-scores">
                                        ${[
                                            {label: 'Cleanliness', score: result.review_scores_cleanliness},
                                            {label: 'Accuracy', score: result.review_scores_accuracy},
                                            {label: 'Communication', score: result.review_scores_communication},
                                            {label: 'Location', score: result.review_scores_location},
                                            {label: 'Check-in', score: result.review_scores_checkin},
                                            {label: 'Value', score: result.review_scores_value}
                                        ].map(item => `
                                            <div class="review-score-item">
                                                <div class="d-flex justify-content-between align-items-center mb-1">
                                                    <span>${item.label}</span>
                                                    <span class="score">${item.score || 'N/A'}</span>
                                                </div>
                                                <div class="progress" style="height: 6px;">
                                                    <div class="progress-bar bg-success" role="progressbar" 
                                                         style="width: ${(item.score / 5) * 100}%" 
                                                         aria-valuenow="${item.score}" 
                                                         aria-valuemin="0" 
                                                         aria-valuemax="5">
                                                    </div>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                
                                <div class="mt-4">
                                    <a href="${result.listing_url}" target="_blank" class="btn airbnb-btn">View on Airbnb</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        resultsContainer.innerHTML = html;

        // Add event listeners for expand buttons
        document.querySelectorAll('.expand-btn').forEach(button => {
            button.addEventListener('click', function() {
                const resultId = this.getAttribute('data-result-id');
                const detailsSection = document.getElementById(`details-${resultId}`);
                const icon = this.querySelector('i');
                
                // Toggle the collapse
                if (detailsSection.classList.contains('show')) {
                    detailsSection.classList.remove('show');
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                } else {
                    detailsSection.classList.add('show');
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                }
            });
        });
    }
});
