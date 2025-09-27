"""
Tests for spaced repetition (SM-2) algorithm
"""

import pytest
from datetime import datetime, timedelta
from app.logic.sr import calculate_next_review, is_due_for_review


class TestCalculateNextReview:
    """Test cases for calculate_next_review function"""
    
    def test_first_review_quality_5(self):
        """Test first review with perfect quality (5)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 5)
        
        assert ease == 2.5 + (0.1 - (5 - 5) * (0.08 + (5 - 5) * 0.02))  # 2.6
        assert interval == 1  # First review
        assert reps == 1
        assert isinstance(next_review, datetime)
        assert next_review > datetime.now()
    
    def test_first_review_quality_4(self):
        """Test first review with good quality (4)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 4)
        
        assert ease == 2.5 + (0.1 - (5 - 4) * (0.08 + (5 - 4) * 0.02))  # 2.5 + 0.1 - 0.1 = 2.5
        assert interval == 1  # First review
        assert reps == 1
        assert isinstance(next_review, datetime)
    
    def test_first_review_quality_3(self):
        """Test first review with passable quality (3)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 3)
        
        assert ease == 2.5 + (0.1 - (5 - 3) * (0.08 + (5 - 3) * 0.02))  # 2.5 + 0.1 - 0.24 = 2.36
        assert interval == 1  # First review
        assert reps == 1
        assert isinstance(next_review, datetime)
    
    def test_first_review_quality_2(self):
        """Test first review with poor quality (2) - should reset"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 2)
        
        assert ease == 1.3  # Reset to minimum
        assert interval == 1  # First review
        assert reps == 0  # Reset repetitions
        assert isinstance(next_review, datetime)
    
    def test_first_review_quality_1(self):
        """Test first review with very poor quality (1) - should reset"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 1)
        
        assert ease == 1.3  # Reset to minimum
        assert interval == 1  # First review
        assert reps == 0  # Reset repetitions
        assert isinstance(next_review, datetime)
    
    def test_second_review_quality_5(self):
        """Test second review with perfect quality (5)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 1, 1, 5)
        
        assert ease > 2.5  # Should increase
        assert interval == 3  # Second review
        assert reps == 2
        assert isinstance(next_review, datetime)
    
    def test_third_review_quality_5(self):
        """Test third review with perfect quality (5)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 3, 2, 5)
        
        assert ease > 2.5  # Should increase
        assert interval == int(2.5 * 3)  # Should be 7
        assert reps == 3
        assert isinstance(next_review, datetime)
    
    def test_poor_quality_resets_reps(self):
        """Test that poor quality resets repetitions"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 2)
        
        assert ease == 1.3  # Reset to minimum
        assert interval == 1  # Reset to first review
        assert reps == 0  # Reset repetitions
        assert isinstance(next_review, datetime)
    
    def test_ease_factor_minimum(self):
        """Test that ease factor never goes below 1.3"""
        ease, interval, reps, next_review = calculate_next_review(1.3, 7, 5, 2)
        
        assert ease == 1.3  # Should stay at minimum
        assert interval == 1  # Reset to first review
        assert reps == 0  # Reset repetitions
    
    def test_ease_factor_calculation_quality_5(self):
        """Test ease factor calculation for quality 5"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 5)
        
        expected_ease = 2.5 + (0.1 - (5 - 5) * (0.08 + (5 - 5) * 0.02))
        assert ease == expected_ease  # Should be 2.6
    
    def test_ease_factor_calculation_quality_4(self):
        """Test ease factor calculation for quality 4"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 4)
        
        expected_ease = 2.5 + (0.1 - (5 - 4) * (0.08 + (5 - 4) * 0.02))
        assert ease == expected_ease  # Should be 2.5
    
    def test_ease_factor_calculation_quality_3(self):
        """Test ease factor calculation for quality 3"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 3)
        
        expected_ease = 2.5 + (0.1 - (5 - 3) * (0.08 + (5 - 3) * 0.02))
        assert ease == expected_ease  # Should be 2.36
    
    def test_interval_calculation_third_review(self):
        """Test interval calculation for third review"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 2, 5)
        
        assert interval == int(2.5 * 7)  # Should be 17
        assert reps == 3
    
    def test_interval_calculation_fourth_review(self):
        """Test interval calculation for fourth review"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 17, 3, 5)
        
        assert interval == int(2.5 * 17)  # Should be 42
        assert reps == 4
    
    def test_quality_0_resets(self):
        """Test that quality 0 resets everything"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 0)
        
        assert ease == 1.3  # Reset to minimum
        assert interval == 1  # Reset to first review
        assert reps == 0  # Reset repetitions
    
    def test_quality_6_handled_gracefully(self):
        """Test that quality 6 is handled gracefully (should be treated as 5)"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, 6)
        
        # Should be treated as quality 5
        assert ease > 2.5
        assert reps == 6
        assert interval > 7


class TestIsDueForReview:
    """Test cases for is_due_for_review function"""
    
    def test_due_for_review_past_date(self):
        """Test that past date is due for review"""
        past_date = datetime.now() - timedelta(days=1)
        assert is_due_for_review(past_date) == True
    
    def test_due_for_review_current_date(self):
        """Test that current date is due for review"""
        current_date = datetime.now()
        assert is_due_for_review(current_date) == True
    
    def test_not_due_for_review_future_date(self):
        """Test that future date is not due for review"""
        future_date = datetime.now() + timedelta(days=1)
        assert is_due_for_review(future_date) == False
    
    def test_not_due_for_review_far_future(self):
        """Test that far future date is not due for review"""
        far_future = datetime.now() + timedelta(days=30)
        assert is_due_for_review(far_future) == False


class TestSM2EdgeCases:
    """Test edge cases for SM-2 algorithm"""
    
    def test_very_high_ease_factor(self):
        """Test with very high ease factor"""
        ease, interval, reps, next_review = calculate_next_review(5.0, 7, 5, 5)
        
        assert ease > 5.0  # Should increase further
        assert interval == int(5.0 * 7)  # Should be 35
        assert reps == 6
    
    def test_very_low_ease_factor(self):
        """Test with very low ease factor"""
        ease, interval, reps, next_review = calculate_next_review(1.3, 7, 5, 5)
        
        assert ease > 1.3  # Should increase
        assert interval == int(1.3 * 7)  # Should be 9
        assert reps == 6
    
    def test_zero_interval(self):
        """Test with zero interval"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 0, 0, 5)
        
        assert interval == 1  # Should be set to 1
        assert reps == 1
    
    def test_negative_interval(self):
        """Test with negative interval"""
        ease, interval, reps, next_review = calculate_next_review(2.5, -1, 0, 5)
        
        assert interval == 1  # Should be set to 1
        assert reps == 1
    
    def test_large_reps_count(self):
        """Test with large repetition count"""
        ease, interval, reps, next_review = calculate_next_review(2.5, 100, 50, 5)
        
        assert ease > 2.5  # Should increase
        assert interval == int(2.5 * 100)  # Should be 250
        assert reps == 51


@pytest.mark.parametrize("quality,expected_reps", [
    (5, 1), (4, 1), (3, 1), (2, 0), (1, 0), (0, 0)
])
def test_reps_calculation(quality, expected_reps):
    """Test repetition calculation for different quality ratings"""
    ease, interval, reps, next_review = calculate_next_review(2.5, 7, 0, quality)
    assert reps == expected_reps


@pytest.mark.parametrize("quality,should_increase_ease", [
    (5, True), (4, True), (3, True), (2, False), (1, False), (0, False)
])
def test_ease_factor_behavior(quality, should_increase_ease):
    """Test ease factor behavior for different quality ratings"""
    ease, interval, reps, next_review = calculate_next_review(2.5, 7, 5, quality)
    
    if should_increase_ease:
        assert ease > 2.5
    else:
        assert ease == 1.3  # Reset to minimum

