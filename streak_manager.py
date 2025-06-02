#!/usr/bin/env python3
"""
Advanced Streak Management System for German Daily Word Bot
Handles streak tracking, milestones, recovery, and motivation features
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class StreakManager:
    def __init__(self, user_progress):
        self.user_progress = user_progress
        self.streak_milestones = [7, 14, 30, 50, 100, 200, 365, 500, 1000]
        self.milestone_rewards = {
            7: {"title": "Week Warrior", "description": "7 days of consistent learning!", "freeze_bonus": 1},
            14: {"title": "Fortnight Fighter", "description": "2 weeks strong!", "freeze_bonus": 1},
            30: {"title": "Monthly Master", "description": "30 days of dedication!", "freeze_bonus": 2},
            50: {"title": "Fifty Fantastic", "description": "50 days of German mastery!", "freeze_bonus": 2},
            100: {"title": "Century Scholar", "description": "100 days of excellence!", "freeze_bonus": 3},
            200: {"title": "Bicentennial Brain", "description": "200 days of linguistic growth!", "freeze_bonus": 3},
            365: {"title": "Annual Achiever", "description": "A full year of German learning!", "freeze_bonus": 5},
            500: {"title": "Quincentennial Genius", "description": "500 days of unwavering commitment!", "freeze_bonus": 5},
            1000: {"title": "Millennium Master", "description": "1000 days of German excellence!", "freeze_bonus": 10}
        }
    
    def update_streak(self, lesson_date: str = None) -> Dict:
        """Update user's learning streak with advanced tracking"""
        if not lesson_date:
            lesson_date = datetime.now().strftime('%Y-%m-%d')
        
        current_date = datetime.strptime(lesson_date, '%Y-%m-%d')
        last_lesson = self.user_progress.data.get('last_lesson_date')
        
        streak_info = {
            'streak_continued': False,
            'streak_broken': False,
            'milestone_reached': None,
            'grace_period_used': False,
            'streak_recovered': False
        }
        
        if not last_lesson:
            # First lesson ever
            self.user_progress.data['daily_streak'] = 1
            self.user_progress.data['total_study_days'] = 1
            streak_info['streak_continued'] = True
        else:
            last_date = datetime.strptime(last_lesson, '%Y-%m-%d')
            days_diff = (current_date - last_date).days
            
            if days_diff == 1:
                # Consecutive day - continue streak
                self.user_progress.data['daily_streak'] += 1
                self.user_progress.data['total_study_days'] += 1
                streak_info['streak_continued'] = True
                
            elif days_diff == 0:
                # Same day - no streak change but count study session
                pass
                
            elif days_diff == 2 and self._can_use_grace_period():
                # One day missed - use grace period
                self.user_progress.data['daily_streak'] += 1
                self.user_progress.data['total_study_days'] += 1
                self._activate_grace_period()
                streak_info['grace_period_used'] = True
                streak_info['streak_continued'] = True
                
            else:
                # Streak broken
                old_streak = self.user_progress.data['daily_streak']
                if old_streak > self.user_progress.data.get('longest_streak', 0):
                    self.user_progress.data['longest_streak'] = old_streak
                
                self.user_progress.data['daily_streak'] = 1
                self.user_progress.data['total_study_days'] += 1
                streak_info['streak_broken'] = True
                
                # Check if streak freeze can be used
                if self._can_use_streak_freeze() and days_diff <= 7:
                    recovered_streak = self._use_streak_freeze(old_streak)
                    if recovered_streak:
                        streak_info['streak_recovered'] = True
                        streak_info['streak_broken'] = False
        
        # Update last lesson date
        self.user_progress.data['last_lesson_date'] = lesson_date
        
        # Check for milestone achievements
        current_streak = self.user_progress.data['daily_streak']
        milestone = self._check_milestone_reached(current_streak)
        if milestone:
            streak_info['milestone_reached'] = milestone
            self._award_milestone(milestone)
        
        # Update longest streak if current is longer
        if current_streak > self.user_progress.data.get('longest_streak', 0):
            self.user_progress.data['longest_streak'] = current_streak
        
        return streak_info
    
    def _can_use_grace_period(self) -> bool:
        """Check if grace period can be activated"""
        return not self.user_progress.data.get('grace_period_active', False)
    
    def _activate_grace_period(self):
        """Activate grace period for streak protection"""
        self.user_progress.data['grace_period_active'] = True
        self.user_progress.data['grace_period_expires'] = (
            datetime.now() + timedelta(days=1)
        ).isoformat()
        logger.info(f"Grace period activated for user {self.user_progress.chat_id}")
    
    def _can_use_streak_freeze(self) -> bool:
        """Check if streak freeze is available"""
        return self.user_progress.data.get('streak_freeze_available', 0) > 0
    
    def _use_streak_freeze(self, old_streak: int) -> bool:
        """Use streak freeze to recover broken streak"""
        if not self._can_use_streak_freeze():
            return False
        
        self.user_progress.data['streak_freeze_available'] -= 1
        self.user_progress.data['streak_freeze_used'] += 1
        self.user_progress.data['daily_streak'] = old_streak + 1
        
        logger.info(f"Streak freeze used for user {self.user_progress.chat_id}, "
                   f"streak recovered to {old_streak + 1}")
        return True
    
    def _check_milestone_reached(self, current_streak: int) -> Optional[int]:
        """Check if a new milestone has been reached"""
        achieved_milestones = self.user_progress.data.get('streak_milestones', [])
        
        for milestone in self.streak_milestones:
            if current_streak >= milestone and milestone not in achieved_milestones:
                return milestone
        return None
    
    def _award_milestone(self, milestone: int):
        """Award milestone achievement and bonuses"""
        if 'streak_milestones' not in self.user_progress.data:
            self.user_progress.data['streak_milestones'] = []
        
        self.user_progress.data['streak_milestones'].append(milestone)
        
        # Add achievement record
        achievement = {
            'type': 'streak_milestone',
            'milestone': milestone,
            'date': datetime.now().isoformat(),
            'title': self.milestone_rewards[milestone]['title'],
            'description': self.milestone_rewards[milestone]['description']
        }
        
        if 'achievements' not in self.user_progress.data:
            self.user_progress.data['achievements'] = []
        
        self.user_progress.data['achievements'].append(achievement)
        
        # Award streak freeze bonus
        freeze_bonus = self.milestone_rewards[milestone].get('freeze_bonus', 0)
        if freeze_bonus > 0:
            current_freezes = self.user_progress.data.get('streak_freeze_available', 0)
            self.user_progress.data['streak_freeze_available'] = current_freezes + freeze_bonus
        
        logger.info(f"Milestone {milestone} awarded to user {self.user_progress.chat_id}")
    
    def get_streak_stats(self) -> Dict:
        """Get comprehensive streak statistics"""
        data = self.user_progress.data
        
        return {
            'current_streak': data.get('daily_streak', 0),
            'longest_streak': data.get('longest_streak', 0),
            'total_study_days': data.get('total_study_days', 0),
            'streak_milestones_achieved': len(data.get('streak_milestones', [])),
            'next_milestone': self._get_next_milestone(),
            'days_to_next_milestone': self._days_to_next_milestone(),
            'streak_freeze_available': data.get('streak_freeze_available', 0),
            'streak_freeze_used': data.get('streak_freeze_used', 0),
            'grace_period_active': data.get('grace_period_active', False),
            'streak_percentage': self._calculate_streak_percentage()
        }
    
    def _get_next_milestone(self) -> Optional[int]:
        """Get the next unachieved milestone"""
        current_streak = self.user_progress.data.get('daily_streak', 0)
        achieved_milestones = self.user_progress.data.get('streak_milestones', [])
        
        for milestone in self.streak_milestones:
            if milestone > current_streak or milestone not in achieved_milestones:
                return milestone
        return None
    
    def _days_to_next_milestone(self) -> Optional[int]:
        """Calculate days remaining to next milestone"""
        next_milestone = self._get_next_milestone()
        if next_milestone:
            current_streak = self.user_progress.data.get('daily_streak', 0)
            return max(0, next_milestone - current_streak)
        return None
    
    def _calculate_streak_percentage(self) -> float:
        """Calculate streak consistency percentage"""
        total_days = self.user_progress.data.get('total_study_days', 0)
        if total_days == 0:
            return 0.0
        
        start_date = datetime.fromisoformat(self.user_progress.data['start_date'])
        days_since_start = (datetime.now() - start_date).days + 1
        
        return min(100.0, (total_days / days_since_start) * 100)
    
    def format_streak_message(self, streak_info: Dict) -> str:
        """Format streak update message for user"""
        stats = self.get_streak_stats()
        message = ""
        
        if streak_info['milestone_reached']:
            milestone = streak_info['milestone_reached']
            reward = self.milestone_rewards[milestone]
            message += f"🎉 **MILESTONE ACHIEVED!** 🎉\n"
            message += f"🏆 {reward['title']}\n"
            message += f"✨ {reward['description']}\n"
            message += f"🛡️ +{reward.get('freeze_bonus', 0)} Streak Freezes!\n\n"
        
        if streak_info['grace_period_used']:
            message += f"🛡️ **Grace Period Used!**\n"
            message += f"Your streak continues thanks to grace period protection!\n\n"
        
        if streak_info['streak_recovered']:
            message += f"❄️ **Streak Freeze Used!**\n"
            message += f"Your streak has been recovered!\n\n"
        
        message += f"🔥 **Current Streak:** {stats['current_streak']} days\n"
        message += f"🏅 **Longest Streak:** {stats['longest_streak']} days\n"
        message += f"📚 **Total Study Days:** {stats['total_study_days']}\n"
        
        if stats['next_milestone']:
            message += f"🎯 **Next Goal:** {stats['next_milestone']} days "
            message += f"({stats['days_to_next_milestone']} to go!)\n"
        
        message += f"🛡️ **Streak Freezes:** {stats['streak_freeze_available']} available\n"
        message += f"📊 **Consistency:** {stats['streak_percentage']:.1f}%"
        
        return message
