// Main JavaScript for Guinée Makiti

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Product image gallery
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.main-product-image');
    
    thumbnails.forEach(function(thumb) {
        thumb.addEventListener('click', function() {
            if (mainImage) {
                mainImage.src = this.src;
            }
        });
    });

    // Search suggestions
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length > 2) {
                // Implement search suggestions here
                fetchSearchSuggestions(query);
            }
        });
    }

    // Add to cart animation
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Ajout...';
            setTimeout(() => {
                this.innerHTML = 'Ajouté !';
                this.classList.remove('btn-primary');
                this.classList.add('btn-success');
            }, 1000);
        });
    });

    // Price range slider
    const priceRange = document.querySelector('#price-range');
    if (priceRange) {
        priceRange.addEventListener('input', function() {
            document.querySelector('#price-display').textContent = this.value + ' GNF';
        });
    }

    // Wishlist toggle
    const wishlistButtons = document.querySelectorAll('.wishlist-toggle');
    wishlistButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            toggleWishlist(productId, this);
        });
    });

    // Rating stars
    const ratingStars = document.querySelectorAll('.rating-star');
    ratingStars.forEach(function(star, index) {
        star.addEventListener('click', function() {
            const rating = index + 1;
            updateRating(rating);
        });
    });
});

// Search suggestions function
function fetchSearchSuggestions(query) {
    fetch(`/products/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchSuggestions(data.suggestions);
        })
        .catch(error => console.error('Error:', error));
}

function displaySearchSuggestions(suggestions) {
    const suggestionsContainer = document.querySelector('#search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.innerHTML = '';
        suggestions.forEach(function(suggestion) {
            const item = document.createElement('div');
            item.className = 'suggestion-item p-2 border-bottom';
            item.textContent = suggestion.name;
            item.addEventListener('click', function() {
                window.location.href = `/products/${suggestion.id}/`;
            });
            suggestionsContainer.appendChild(item);
        });
    }
}

// Wishlist toggle function
function toggleWishlist(productId, button) {
    const isInWishlist = button.classList.contains('in-wishlist');
    const url = isInWishlist ? 
        `/products/wishlist/remove/${productId}/` : 
        `/products/wishlist/add/${productId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.toggle('in-wishlist');
            const icon = button.querySelector('i');
            if (button.classList.contains('in-wishlist')) {
                icon.className = 'fas fa-heart text-danger';
                button.title = 'Retirer des favoris';
            } else {
                icon.className = 'far fa-heart';
                button.title = 'Ajouter aux favoris';
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Rating update function
function updateRating(rating) {
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach(function(star, index) {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
    document.querySelector('#rating-input').value = rating;
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Geolocation for delivery
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById('delivery_lat').value = position.coords.latitude;
            document.getElementById('delivery_lng').value = position.coords.longitude;
            
            // Reverse geocoding to get address
            reverseGeocode(position.coords.latitude, position.coords.longitude);
        }, function(error) {
            console.error('Geolocation error:', error);
            alert('Impossible d\'obtenir votre position. Veuillez saisir votre adresse manuellement.');
        });
    } else {
        alert('La géolocalisation n\'est pas supportée par ce navigateur.');
    }
}

function reverseGeocode(lat, lng) {
    // Using OpenStreetMap Nominatim API for reverse geocoding
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
        .then(response => response.json())
        .then(data => {
            if (data.display_name) {
                document.getElementById('delivery_address').value = data.display_name;
            }
        })
        .catch(error => console.error('Reverse geocoding error:', error));
}

// Product comparison
function addToComparison(productId) {
    let comparison = JSON.parse(localStorage.getItem('comparison') || '[]');
    if (!comparison.includes(productId)) {
        comparison.push(productId);
        if (comparison.length > 4) {
            comparison = comparison.slice(-4); // Keep only last 4 products
        }
        localStorage.setItem('comparison', JSON.stringify(comparison));
        updateComparisonCounter();
    }
}

function removeFromComparison(productId) {
    let comparison = JSON.parse(localStorage.getItem('comparison') || '[]');
    comparison = comparison.filter(id => id !== productId);
    localStorage.setItem('comparison', JSON.stringify(comparison));
    updateComparisonCounter();
}

function updateComparisonCounter() {
    const comparison = JSON.parse(localStorage.getItem('comparison') || '[]');
    const counter = document.querySelector('#comparison-counter');
    if (counter) {
        counter.textContent = comparison.length;
        counter.style.display = comparison.length > 0 ? 'inline' : 'none';
    }
}

// Initialize comparison counter on page load
updateComparisonCounter();

// Live chat functionality
function initializeChat() {
    const chatButton = document.querySelector('#chat-button');
    const chatWindow = document.querySelector('#chat-window');
    
    if (chatButton && chatWindow) {
        chatButton.addEventListener('click', function() {
            chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
        });
    }
}

// Currency formatter for Guinea Franc
function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-GN', {
        style: 'currency',
        currency: 'GNF',
        minimumFractionDigits: 0
    }).format(amount);
}

// Initialize chat on page load
initializeChat();