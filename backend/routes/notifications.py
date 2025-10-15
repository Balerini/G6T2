from flask import Blueprint, jsonify, request
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.notification_service import notification_service

notifications_bp = Blueprint('notifications', __name__)

# =============== GET USER NOTIFICATIONS ===============
@notifications_bp.route('/api/notifications/<user_id>', methods=['GET'])
def get_user_notifications(user_id):
    """Get notifications for a specific user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only
        )
        
        return jsonify({
            'notifications': notifications,
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting notifications for user {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== MARK NOTIFICATION AS READ ===============
@notifications_bp.route('/api/notifications/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        success = notification_service.mark_as_read(notification_id)
        
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        print(f"❌ Error marking notification as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== MARK ALL NOTIFICATIONS AS READ ===============
@notifications_bp.route('/api/notifications/user/<user_id>/read-all', methods=['PUT'])
def mark_all_notifications_read(user_id):
    """Mark all notifications for a user as read"""
    try:
        count = notification_service.mark_all_as_read(user_id)
        
        return jsonify({
            'message': f'{count} notifications marked as read',
            'count': count
        }), 200
        
    except Exception as e:
        print(f"❌ Error marking all notifications as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== DELETE NOTIFICATION ===============
@notifications_bp.route('/api/notifications/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        success = notification_service.delete_notification(notification_id)
        
        if success:
            return jsonify({'message': 'Notification deleted'}), 200
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        print(f"❌ Error deleting notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== TRIGGER DEADLINE CHECK ===============
@notifications_bp.route('/api/notifications/check-deadlines', methods=['POST'])
def check_deadlines():
    """Manually trigger deadline check for upcoming tasks"""
    try:
        print("🔔 Manual deadline check triggered")
        notification_count = notification_service.notify_upcoming_deadlines()
        
        return jsonify({
            'message': 'Deadline check completed',
            'notifications_sent': notification_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error checking deadlines: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== TRIGGER OVERDUE CHECK ===============
@notifications_bp.route('/api/notifications/check-overdue', methods=['POST'])
def check_overdue():
    """Manually trigger overdue task check"""
    try:
        print("🚨 Manual overdue check triggered")
        notification_count = notification_service.notify_overdue_tasks()
        
        return jsonify({
            'message': 'Overdue check completed',
            'notifications_sent': notification_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error checking overdue tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== TRIGGER ALL CHECKS ===============
@notifications_bp.route('/api/notifications/check-all', methods=['POST'])
def check_all():
    """Manually trigger all notification checks"""
    try:
        print("🔔 Manual notification check triggered")
        
        # Check upcoming deadlines
        deadline_count = notification_service.notify_upcoming_deadlines()
        
        # Check overdue tasks
        overdue_count = notification_service.notify_overdue_tasks()
        
        return jsonify({
            'message': 'All notification checks completed',
            'deadline_notifications': deadline_count,
            'overdue_notifications': overdue_count,
            'total_notifications': deadline_count + overdue_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error checking all notifications: {str(e)}")
        return jsonify({'error': str(e)}), 500
