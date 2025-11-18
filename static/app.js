/**
 * TravelMind Frontend JavaScript
 *
 * Handles form submission, API calls, loading states, and itinerary rendering.
 */

// State management
let currentItinerary = null;

/**
 * Fill the textarea with an example query
 */
function fillExample(exampleText) {
    document.getElementById('queryInput').value = exampleText;
}

/**
 * Handle form submission
 */
async function handleSubmit(event) {
    event.preventDefault();

    const query = document.getElementById('queryInput').value.trim();
    if (!query) return;

    // Hide any previous results or errors
    hideResults();
    hideError();

    // Show loading state
    showLoading();

    // Simulate progress steps
    simulateProgress();

    try {
        // Make API request
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        // Hide loading
        hideLoading();

        if (data.success) {
            // Show results
            currentItinerary = data.itinerary;
            renderItinerary(data.itinerary);
            showResults();
        } else {
            // Show error
            showError(data.error_type || 'Error', data.error || 'An unknown error occurred');
        }

    } catch (error) {
        hideLoading();
        showError('Network Error', `Failed to connect to server: ${error.message}`);
    }
}

/**
 * Simulate progress through workflow steps
 */
function simulateProgress() {
    const steps = ['step-intent', 'step-poi', 'step-weather', 'step-itinerary'];
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepEl = document.getElementById(steps[currentStep]);
            stepEl.classList.add('active');

            if (currentStep > 0) {
                const prevStep = document.getElementById(steps[currentStep - 1]);
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
            }

            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 1500);
}

/**
 * Show loading state
 */
function showLoading() {
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('submitBtn').disabled = true;

    // Reset progress steps
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed');
    });
}

/**
 * Hide loading state
 */
function hideLoading() {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('submitBtn').disabled = false;
}

/**
 * Show error message
 */
function showError(errorType, errorMessage) {
    document.getElementById('errorTitle').textContent = errorType;
    document.getElementById('errorMessage').textContent = errorMessage;
    document.getElementById('errorDisplay').style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    document.getElementById('errorDisplay').style.display = 'none';
}

/**
 * Show results section
 */
function showResults() {
    document.getElementById('resultsSection').style.display = 'block';
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Hide results section
 */
function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

/**
 * Reset form to initial state
 */
function resetForm() {
    hideResults();
    hideError();
    document.getElementById('queryInput').value = '';
    document.getElementById('queryInput').focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Render the complete itinerary
 */
function renderItinerary(itinerary) {
    const container = document.getElementById('itineraryContent');
    container.innerHTML = '';

    // Render summary
    const summary = renderSummary(itinerary);
    container.appendChild(summary);

    // Render each day
    itinerary.days.forEach((day, index) => {
        const dayCard = renderDay(day, index + 1);
        container.appendChild(dayCard);
    });
}

/**
 * Render itinerary summary
 */
function renderSummary(itinerary) {
    const div = document.createElement('div');
    div.className = 'itinerary-summary';

    div.innerHTML = `
        <h3>Trip Summary</h3>
        <div class="summary-stats">
            <div class="stat">
                <span class="stat-icon">📅</span>
                <span>${itinerary.total_days} days</span>
            </div>
            <div class="stat">
                <span class="stat-icon">📍</span>
                <span>${itinerary.total_pois} attractions</span>
            </div>
            <div class="stat">
                <span class="stat-icon">🚶</span>
                <span>${itinerary.total_distance_km.toFixed(1)} km total</span>
            </div>
        </div>
    `;

    return div;
}

/**
 * Render a single day card
 */
function renderDay(day, dayNumber) {
    const div = document.createElement('div');
    div.className = 'day-card';

    // Get weather emoji
    const weatherEmoji = getWeatherEmoji(day.weather.category);

    div.innerHTML = `
        <div class="day-header">
            <h3 class="day-title">Day ${dayNumber} - ${formatDate(day.date)}</h3>
            <div class="weather-badge">
                <span>${weatherEmoji}</span>
                <span>${day.weather.description}</span>
            </div>
        </div>

        <div class="day-stats">
            <p><strong>📍 ${day.pois_count} attractions</strong> • ${day.total_distance_km.toFixed(1)} km walking</p>
        </div>

        <div class="timeline">
            ${renderTimeline(day.timeline)}
        </div>
    `;

    return div;
}

/**
 * Render timeline events for a day
 */
function renderTimeline(timeline) {
    return timeline.map(event => {
        if (event.type === 'poi') {
            return `
                <div class="timeline-item">
                    <div class="time">${event.time}</div>
                    <div class="event-details">
                        <div class="event-name">📍 ${event.name}</div>
                        <div class="event-category">${event.category}</div>
                    </div>
                </div>
            `;
        } else if (event.type === 'travel') {
            return `
                <div class="timeline-item">
                    <div class="time">${event.time}</div>
                    <div class="event-details">
                        <div class="event-name">🚶 Walk to next location</div>
                        <div class="event-category">${event.distance_km.toFixed(2)} km • ${event.duration_minutes} min</div>
                    </div>
                </div>
            `;
        }
        return '';
    }).join('');
}

/**
 * Get weather emoji based on category
 */
function getWeatherEmoji(category) {
    const emojiMap = {
        'excellent': '☀️',
        'good': '⛅',
        'fair': '🌤️',
        'indoor': '🌧️',
        'challenging': '⛈️'
    };
    return emojiMap[category] || '🌤️';
}

/**
 * Format date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Auto-focus on textarea when page loads
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('queryInput').focus();
});
