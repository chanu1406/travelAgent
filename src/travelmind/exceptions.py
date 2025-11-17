"""
Custom exceptions for TravelMind application.

These exceptions provide better error messages and allow for more granular error handling.
"""


class TravelMindError(Exception):
    """Base exception for all TravelMind errors."""

    pass


# ============================================================================
# Intent Agent Errors
# ============================================================================


class IntentParsingError(TravelMindError):
    """Raised when intent parsing fails."""

    pass


class InvalidDateError(TravelMindError):
    """Raised when dates are invalid (e.g., in the past, end before start)."""

    pass


class InvalidDurationError(TravelMindError):
    """Raised when trip duration is invalid (e.g., too short, too long)."""

    pass


class MissingDestinationError(TravelMindError):
    """Raised when no destination is provided."""

    pass


# ============================================================================
# POI Agent Errors
# ============================================================================


class POISearchError(TravelMindError):
    """Raised when POI search fails."""

    pass


class NoPOIsFoundError(TravelMindError):
    """Raised when no POIs are found for the given criteria."""

    pass


class GeoapifyAPIError(TravelMindError):
    """Raised when Geoapify API returns an error."""

    pass


# ============================================================================
# Weather Agent Errors
# ============================================================================


class WeatherAPIError(TravelMindError):
    """Raised when weather API fails."""

    pass


class WeatherDataUnavailableError(TravelMindError):
    """Raised when weather data is not available for the requested dates."""

    pass


# ============================================================================
# Route Agent Errors
# ============================================================================


class RouteOptimizationError(TravelMindError):
    """Raised when route optimization fails."""

    pass


class DistanceCalculationError(TravelMindError):
    """Raised when distance calculation fails."""

    pass


# ============================================================================
# Calendar Agent Errors
# ============================================================================


class ItineraryBuildError(TravelMindError):
    """Raised when itinerary building fails."""

    pass


class InsufficientPOIsError(TravelMindError):
    """Raised when there are not enough POIs to build an itinerary."""

    pass


# ============================================================================
# Export Agent Errors
# ============================================================================


class ExportError(TravelMindError):
    """Raised when export fails."""

    pass


class UnsupportedFormatError(TravelMindError):
    """Raised when an unsupported export format is requested."""

    pass
