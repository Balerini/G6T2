from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client
from firebase_admin import firestore
from datetime import datetime, timedelta
import calendar
import traceback
import pytz
import sys
import os

# Add parent directory to path for importsx 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.notification_service import notification_service


tasks_bp = Blueprint('tasks', __name__)

def _parse_date_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return None
    return None


def _add_months(base_dt, months):
    month_index = base_dt.month - 1 + months
    year = base_dt.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base_dt.day, calendar.monthrange(year, month)[1])
    return base_dt.replace(year=year, month=month, day=day)


def _compute_next_occurrence_dates(current_start_dt, current_end_dt, recurrence_info):
    if current_start_dt is None:
        return None, None

    freq = (recurrence_info.get('frequency') or 'daily').lower()
    try:
        interval = int(recurrence_info.get('interval') or 1)
    except (TypeError, ValueError):
        interval = 1
    interval = max(1, interval)

    def apply_duration(next_start_dt):
        if current_end_dt and isinstance(current_end_dt, datetime):
            duration = current_end_dt - current_start_dt
            return next_start_dt, next_start_dt + duration
        return next_start_dt, None

    if freq == 'daily':
        return apply_duration(current_start_dt + timedelta(days=interval))

    if freq == 'weekly':
        weekly_days = recurrence_info.get('weeklyDays') or []
        normalized_days = []
        for entry in weekly_days:
            try:
                normalized_days.append(int(str(entry)))
            except (TypeError, ValueError):
                continue
        normalized_days = sorted({d for d in normalized_days if 0 <= d <= 6})
        if not normalized_days:
            normalized_days = [current_start_dt.weekday()]

        current_weekday = current_start_dt.weekday()
        for day in normalized_days:
            if day > current_weekday:
                delta_days = day - current_weekday
                return apply_duration(current_start_dt + timedelta(days=delta_days))

        delta_weeks = interval - 1
        delta_days = (7 * delta_weeks) + ((7 - current_weekday) + normalized_days[0])
        return apply_duration(current_start_dt + timedelta(days=delta_days))

    if freq == 'monthly':
        next_start = _add_months(current_start_dt, interval)
        monthly_day = recurrence_info.get('monthlyDay')
        if monthly_day not in (None, '', 0):
            try:
                monthly_day = int(monthly_day)
                monthly_day = max(1, min(31, monthly_day))
                days_in_month = calendar.monthrange(next_start.year, next_start.month)[1]
                next_start = next_start.replace(day=min(monthly_day, days_in_month))
            except (TypeError, ValueError):
                pass
        return apply_duration(next_start)

    if freq == 'custom':
        unit = (recurrence_info.get('customUnit') or 'days').lower()
        if unit in ('week', 'weeks'):
            return apply_duration(current_start_dt + timedelta(days=7 * interval))
        if unit in ('month', 'months'):
            return apply_duration(_add_months(current_start_dt, interval))
        return apply_duration(current_start_dt + timedelta(days=interval))

    return apply_duration(current_start_dt + timedelta(days=interval))


def _should_stop_recurrence(recurrence_info, next_occurrence_index, next_start_dt):
    end_condition = (recurrence_info.get('endCondition') or 'never').lower()
    if end_condition == 'after':
        try:
            max_occurrences = int(recurrence_info.get('endAfterOccurrences') or 0)
        except (TypeError, ValueError):
            max_occurrences = 0
        if max_occurrences and next_occurrence_index > max_occurrences:
            return True
    elif end_condition == 'ondate':
        end_date_value = recurrence_info.get('endDate')
        end_date = _parse_date_value(end_date_value)
        if end_date and next_start_dt and next_start_dt.date() > end_date:
            return True
    return False


# =============== CREATE TASK ===============
@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        task_data = request.get_json()
        print("BACKEND TASK CREATION DEBUG")
        print(f"Received task data: {task_data}")
        print(f"Priority level received: {task_data.get('priority_level')}")  # Changed to priority_level

        # Validate required fields
        required_fields = ['task_name', 'start_date', 'priority_level']  # Changed to priority_level
        for field in required_fields:
            if not task_data.get(field):
                return jsonify({"error": f"Required field missing: {field}"}), 400

        # Validate priority level range
        try:
            priority_level = int(task_data.get('priority_level'))  # Changed variable name
            if priority_level < 1 or priority_level > 10:
                return jsonify({"error": "Priority level must be between 1 and 10"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Priority level must be a valid number between 1 and 10"}), 400

        # TITLE: Validate priority level range
        db = get_firestore_client()

        # Get creator ID early so we can use it throughout
        owner_id = task_data.get('owner', '')

        # Convert date strings to datetime objects with Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        start_date = datetime.strptime(task_data['start_date'], '%Y-%m-%d')
        start_date = sg_tz.localize(start_date)
        
        end_date = None
        if task_data.get('end_date'):
            end_date = datetime.strptime(task_data['end_date'], '%Y-%m-%d')
            # Set to start of day (12:00 AM) instead of end of day (11:59 PM)
            end_date = sg_tz.localize(end_date.replace(hour=0, minute=0, second=0))

        # Helper for parsing project/task end dates
        def add_months(base_dt, months):
            month_index = base_dt.month - 1 + months
            year = base_dt.year + month_index // 12
            month = month_index % 12 + 1
            day = min(base_dt.day, calendar.monthrange(year, month)[1])
            return base_dt.replace(year=year, month=month, day=day)

        def compute_next_occurrence_dates(current_start_dt, current_end_dt, recurrence_info):
            if current_start_dt is None:
                return None, None

            freq = (recurrence_info.get('frequency') or 'daily').lower()
            try:
                interval = int(recurrence_info.get('interval') or 1)
            except (TypeError, ValueError):
                interval = 1
            interval = max(1, interval)

            def apply_duration(next_start_dt):
                if current_end_dt and isinstance(current_end_dt, datetime):
                    duration = current_end_dt - current_start_dt
                    return next_start_dt, next_start_dt + duration
                return next_start_dt, None

            if freq == 'daily':
                return apply_duration(current_start_dt + timedelta(days=interval))

            if freq == 'weekly':
                weekly_days = recurrence_info.get('weeklyDays') or []
                normalized_days = []
                for entry in weekly_days:
                    try:
                        normalized_days.append(int(str(entry)))
                    except (TypeError, ValueError):
                        continue
                normalized_days = sorted({d for d in normalized_days if 0 <= d <= 6})
                if not normalized_days:
                    normalized_days = [current_start_dt.weekday()]

                current_weekday = current_start_dt.weekday()
                for day in normalized_days:
                    if day > current_weekday:
                        delta_days = day - current_weekday
                        return apply_duration(current_start_dt + timedelta(days=delta_days))

                delta_weeks = interval - 1
                delta_days = (7 * delta_weeks) + ((7 - current_weekday) + normalized_days[0])
                return apply_duration(current_start_dt + timedelta(days=delta_days))

            if freq == 'monthly':
                next_start = add_months(current_start_dt, interval)
                monthly_day = recurrence_info.get('monthlyDay')
                if monthly_day not in (None, '', 0):
                    try:
                        monthly_day = int(monthly_day)
                        monthly_day = max(1, min(31, monthly_day))
                        days_in_month = calendar.monthrange(next_start.year, next_start.month)[1]
                        next_start = next_start.replace(day=min(monthly_day, days_in_month))
                    except (TypeError, ValueError):
                        pass
                return apply_duration(next_start)

            if freq == 'custom':
                unit = (recurrence_info.get('customUnit') or 'days').lower()
                if unit in ('week', 'weeks'):
                    return apply_duration(current_start_dt + timedelta(days=7 * interval))
                if unit in ('month', 'months'):
                    return apply_duration(add_months(current_start_dt, interval))
                return apply_duration(current_start_dt + timedelta(days=interval))

            # Default fallback behaves like daily
            return apply_duration(current_start_dt + timedelta(days=interval))

        def should_stop_recurrence(recurrence_info, next_occurrence_index, next_start_dt):
            end_condition = (recurrence_info.get('endCondition') or 'never').lower()
            if end_condition == 'after':
                try:
                    max_occurrences = int(recurrence_info.get('endAfterOccurrences') or 0)
                except (TypeError, ValueError):
                    max_occurrences = 0
                if max_occurrences and next_occurrence_index > max_occurrences:
                    return True
            elif end_condition == 'ondate':
                end_date_value = recurrence_info.get('endDate')
                end_date = _parse_date_value(end_date_value)
                if end_date and next_start_dt and next_start_dt.date() > end_date:
                    return True
            return False

        project_end_limit = None
        # Get project ID from project name if provided
        proj_id = None
        if task_data.get('proj_name'):
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_name', '==', task_data.get('proj_name')).limit(1)
            project_docs = list(projects_query.stream())
            
            if project_docs:
                proj_id = project_docs[0].id
                print(f"Found project ID: {proj_id} for project name: {task_data.get('proj_name')}")
                try:
                    project_doc_data = project_docs[0].to_dict() or {}
                except Exception:
                    project_doc_data = {}
                raw_project_end = (
                    project_doc_data.get('end_date')
                    or project_doc_data.get('proj_end_date')
                    or project_doc_data.get('project_end_date')
                )
                project_end_limit = _parse_date_value(raw_project_end)
            else:
                print(f"Warning: Project not found for name: {task_data.get('proj_name')}")
                all_projects = projects_ref.stream()
                print("Available projects:")
                for proj in all_projects:
                    proj_data = proj.to_dict()
                    print(f" - ID: {proj.id}, Name: {proj_data.get('proj_name', 'No name')}")
        else:
            print("No project name provided in task data")

        if project_end_limit is None:
            fallback_project_end = (
                task_data.get('proj_end_date')
                or task_data.get('project_end_date')
                or task_data.get('proj_endDate')
                or task_data.get('project_endDate')
            )
            project_end_limit = _parse_date_value(fallback_project_end)

        recurrence_payload = task_data.get('recurrence')
        recurrence_data = {'enabled': False}

        if recurrence_payload is not None:
            if not isinstance(recurrence_payload, dict):
                return jsonify({"error": "Invalid recurrence payload"}), 400

            normalized_recurrence = dict(recurrence_payload)
            normalized_recurrence['enabled'] = bool(normalized_recurrence.get('enabled'))

            if normalized_recurrence['enabled']:
                if 'end_condition' in normalized_recurrence:
                    normalized_recurrence['endCondition'] = normalized_recurrence.pop('end_condition')
                if 'end_date' in normalized_recurrence:
                    normalized_recurrence['endDate'] = normalized_recurrence.pop('end_date')
                if 'weekly_days' in normalized_recurrence and 'weeklyDays' not in normalized_recurrence:
                    normalized_recurrence['weeklyDays'] = normalized_recurrence.pop('weekly_days')
                if 'monthly_day' in normalized_recurrence and 'monthlyDay' not in normalized_recurrence:
                    normalized_recurrence['monthlyDay'] = normalized_recurrence.pop('monthly_day')
                if 'custom_unit' in normalized_recurrence and 'customUnit' not in normalized_recurrence:
                    normalized_recurrence['customUnit'] = normalized_recurrence.pop('custom_unit')
                if 'end_after_occurrences' in normalized_recurrence and 'endAfterOccurrences' not in normalized_recurrence:
                    normalized_recurrence['endAfterOccurrences'] = normalized_recurrence.pop('end_after_occurrences')

                frequency_value = normalized_recurrence.get('frequency')
                normalized_recurrence['frequency'] = str(frequency_value).lower() if frequency_value else ''

                allowed_frequencies = {'daily', 'weekly', 'monthly', 'custom'}
                if not normalized_recurrence['frequency']:
                    return jsonify({"error": "Recurrence frequency is required when recurrence is enabled"}), 400
                if normalized_recurrence['frequency'] not in allowed_frequencies:
                    return jsonify({"error": f"Invalid recurrence frequency: {normalized_recurrence['frequency']}"}), 400

                try:
                    normalized_recurrence['interval'] = max(1, int(normalized_recurrence.get('interval') or 1))
                except (ValueError, TypeError):
                    normalized_recurrence['interval'] = 1

                if normalized_recurrence['frequency'] == 'weekly':
                    weekly_days = normalized_recurrence.get('weeklyDays') or []
                    if isinstance(weekly_days, list):
                        normalized_recurrence['weeklyDays'] = [str(day) for day in weekly_days if day]
                    else:
                        normalized_recurrence['weeklyDays'] = []
                else:
                    normalized_recurrence.pop('weeklyDays', None)

                if normalized_recurrence['frequency'] == 'monthly':
                    monthly_day = normalized_recurrence.get('monthlyDay')
                    if monthly_day in (None, '', 0):
                        normalized_recurrence['monthlyDay'] = None
                    else:
                        try:
                            normalized_recurrence['monthlyDay'] = int(monthly_day)
                        except (ValueError, TypeError):
                            return jsonify({"error": "Invalid monthly recurrence configuration"}), 400
                else:
                    normalized_recurrence.pop('monthlyDay', None)

                if normalized_recurrence['frequency'] == 'custom':
                    normalized_recurrence['customUnit'] = normalized_recurrence.get('customUnit', 'days')
                else:
                    normalized_recurrence.pop('customUnit', None)

                end_condition_value = normalized_recurrence.get('endCondition') or 'never'
                end_condition_value = str(end_condition_value)
                if end_condition_value not in {'never', 'after', 'onDate'}:
                    end_condition_value = 'never'
                normalized_recurrence['endCondition'] = end_condition_value

                if end_condition_value == 'after':
                    try:
                        occurrences = int(normalized_recurrence.get('endAfterOccurrences') or 0)
                        if occurrences < 1:
                            raise ValueError
                        normalized_recurrence['endAfterOccurrences'] = occurrences
                    except (ValueError, TypeError):
                        return jsonify({"error": "Recurrence endAfterOccurrences must be a positive number"}), 400
                    normalized_recurrence.pop('endDate', None)
                elif end_condition_value == 'onDate':
                    end_date_value = normalized_recurrence.get('endDate')
                    parsed_end_date = _parse_date_value(end_date_value)
                    if parsed_end_date is None:
                        return jsonify({"error": "Invalid recurrence endDate"}), 400
                    if project_end_limit and parsed_end_date > project_end_limit:
                        parsed_end_date = project_end_limit
                    normalized_recurrence['endDate'] = parsed_end_date.isoformat()
                    normalized_recurrence.pop('endAfterOccurrences', None)
                else:
                    normalized_recurrence.pop('endAfterOccurrences', None)
                    normalized_recurrence.pop('endDate', None)

                recurrence_data = normalized_recurrence
            else:
                recurrence_data = {'enabled': False}

        # Prepare task data for Firestore
        firestore_task_data = {
            'proj_name': task_data.get('proj_name', ''),
            'proj_ID': proj_id,
            'task_name': task_data['task_name'],
            'task_desc': task_data.get('task_desc', ''),
            'start_date': start_date,
            'end_date': end_date,
            'owner': owner_id,
            'assigned_to': task_data.get('assigned_to', []),
            'attachments': task_data.get('attachments', []),
            'task_status': task_data.get('task_status'),
            'priority_level': priority_level,
            'hasSubtasks': task_data.get('hasSubtasks', False),
            'is_deleted': task_data.get('is_deleted', False), 
            'recurrence': recurrence_data,
            'recurrence_occurrence': 1 if recurrence_data.get('enabled') else None,
            'recurrence_series_id': None,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }

        print(f"Adding task to Firestore: {firestore_task_data}")
        print(f"Creating task '{firestore_task_data['task_name']}' with assigned_to: {task_data.get('assigned_to', [])}")

        # Add document to Firestore
        doc_ref = db.collection('Tasks').add(firestore_task_data)
        task_ref = doc_ref[1]
        task_id = task_ref.id
        if firestore_task_data['recurrence_occurrence']:
            try:
                task_ref.update({'recurrence_series_id': task_id})
            except Exception:
                pass
        print(f"Task created successfully with ID: {task_id}")

        # Prepare response data
        response_data = firestore_task_data.copy()
        response_data['id'] = task_id
        if response_data.get('recurrence_occurrence'):
            response_data['recurrence_series_id'] = task_id
        response_data['start_date'] = start_date.isoformat()
        if end_date:
            response_data['end_date'] = end_date.isoformat()
        response_data['createdAt'] = datetime.now(sg_tz).isoformat()
        response_data['updatedAt'] = datetime.now(sg_tz).isoformat()
        response_data['proj_ID'] = proj_id
        response_data['recurrence'] = recurrence_data

        # ================== SEND EMAILS TO ASSIGNED USERS ==================
        try:
            from services.email_service import email_service

            # Get creator's info (for the "owner" field)
            creator_name = 'Unknown User'
            if owner_id:
                creator_doc = db.collection('Users').document(owner_id).get()
                creator_name = creator_doc.to_dict().get('name', 'Unknown User') if creator_doc.exists else 'Unknown User'

            # Send emails to each assigned user (except creator)
            assigned_users = task_data.get('assigned_to', []) 
            for user_id in assigned_users:
                if user_id == owner_id:
                    continue

                user_doc = db.collection('Users').document(user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    to_email = user_data.get('email')
                    user_name = user_data.get('name', 'User')

                    if to_email:
                        email_service.send_task_assignment_email(
                            to_email=to_email,
                            user_name=user_name,
                            task_name=firestore_task_data['task_name'],
                            task_desc=firestore_task_data.get('task_desc', ''),
                            project_name=firestore_task_data.get('proj_name', ''),
                            creator_name=creator_name,
                            start_date=str(firestore_task_data['start_date'].date()),
                            end_date=str(firestore_task_data['end_date'].date()) if firestore_task_data.get('end_date') else None,
                            priority_level=firestore_task_data.get('priority_level', '')  
                        )
                    else:
                        print(f"⚠️ No email found for user {user_id}")
        except Exception as e:
            print(f"❌ Failed to send email notifications: {e}")

        # ================== CREATE NOTIFICATIONS FOR STAFF ==================
        try:
            # Notify assigned staff members about task assignment
            assigned_users = task_data.get('assigned_to', [])
            if assigned_users:
                notification_task_data = {
                    'task_name': firestore_task_data['task_name'],
                    'task_ID': task_id,
                    'id': task_id,
                    'proj_ID': proj_id
                }
                notification_service.notify_task_assigned(notification_task_data, assigned_users)
                print(f"✅ Notifications created for {len(assigned_users)} assigned users")
        except Exception as e:
            print(f"❌ Failed to create notifications: {e}")

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        db = get_firestore_client()
        print("entered app.py")
        user_id = request.args.get("userId")
        tasks_ref = db.collection("Tasks")

        # Collect status filters from query params (supports repeated and comma-separated values)
        raw_status_filters = []
        for key in ("status", "statuses"):
            values = request.args.getlist(key)
            if values:
                raw_status_filters.extend(values)
            else:
                single_value = request.args.get(key)
                if single_value:
                    raw_status_filters.append(single_value)

        status_groups = {
            "active": {"active", "unassigned", "ongoing", "under review"}
        }

        def parse_status_tokens(tokens):
            processed = []
            for token in tokens:
                if not token:
                    continue
                processed.extend(part.strip() for part in token.split(",") if part.strip())

            lowered = {token.lower() for token in processed}
            if not lowered or "all" in lowered:
                return None

            expanded = set()
            for token in lowered:
                if token in status_groups:
                    expanded.update(status_groups[token])
                else:
                    expanded.add(token)
            return expanded

        allowed_statuses = parse_status_tokens(raw_status_filters)

        def include_task(task_dict):
            if allowed_statuses is None:
                return True

            status_value = task_dict.get("task_status") or task_dict.get("status") or ""
            if not isinstance(status_value, str):
                status_value = str(status_value)
            status_value = status_value.strip() or "Unassigned"
            return status_value.lower() in allowed_statuses

        tasks = []

        if user_id:
            assigned_query = tasks_ref.where("assigned_to", "array_contains", user_id)
            assigned_results = assigned_query.stream()

            owner_query = tasks_ref.where("owner", "==", user_id)
            owner_results = owner_query.stream()

            seen_ids = set()
            for doc in assigned_results:
                if doc.id not in seen_ids:
                    task = doc.to_dict()
                    task["id"] = doc.id
                    
                    # Filter out deleted tasks and enforce user filters
                    if not task.get("is_deleted", False):
                        if include_task(task):
                            tasks.append(task)
                            seen_ids.add(doc.id)

            for doc in owner_results:
                if doc.id not in seen_ids:
                    task = doc.to_dict()
                    task["id"] = doc.id
                    
                    # Filter out deleted tasks and enforce user filters
                    if not task.get("is_deleted", False):
                        if include_task(task):
                            tasks.append(task)
                            seen_ids.add(doc.id)

        else:
            # If no user_id provided, return all tasks
            results = tasks_ref.stream()
            for doc in results:
                task = doc.to_dict()
                task["id"] = doc.id
                
                if not task.get('is_deleted', False):
                    if include_task(task):
                        tasks.append(task)

        return jsonify(tasks), 200

    except Exception as e:
        print("Error fetching tasks:", e)
        return jsonify({"error": str(e)}), 500

# =============== GET SINGLE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        doc = doc_ref.get()

        if doc.exists:
            task_data = doc.to_dict()
            task_data['id'] = doc.id
            
            # Convert timestamps to ISO format
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()

            return jsonify(task_data), 200
        else:
            return jsonify({'error': 'Task not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== UPDATE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task.

    URL Param:
      task_id: Either Firestore document id or business task_ID.

    Body (JSON): Partial update. Recognized fields include
      - proj_ID, task_ID, task_name, task_desc
      - start_date (YYYY-MM-DD)
      - end_date   (YYYY-MM-DD)
      - task_status
      - assigned_to (array)
      - status_log: optional array with a single entry
          { changed_by, timestamp (ISO), new_status }

    Notes:
      - Dates are converted to Firestore timestamps (end date set to end-of-day)
      - If task_id is not a valid document id, resolves by task_ID (and proj_ID if provided)
      - status_log is appended (ArrayUnion) instead of overwriting
      - Sends email to new owner and CC's old owner when ownership changes
    """
    try:
        print(f"\n🔧 === UPDATE TASK CALLED === Task ID: {task_id}")
        incoming_data = request.get_json() or {}
        if not isinstance(incoming_data, dict):
            return jsonify({"error": "Invalid payload format"}), 400

        print(f"📦 Update data received: {list(incoming_data.keys())}")

        current_user_id = str(request.headers.get('X-User-Id', '')).strip()
        current_user_role = request.headers.get('X-User-Role')
        current_user_name = str(request.headers.get('X-User-Name', '') or '').strip()
        print(f"👤 Update requested by user_id={current_user_id} role={current_user_role}")

        if not current_user_id:
            return jsonify({"error": "Missing user context"}), 400

        db = get_firestore_client()
        update_data = dict(incoming_data)
        
        # Handle date conversion if dates are being updated with Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        
        if 'start_date' in update_data and update_data['start_date']:
            start_date = datetime.strptime(update_data['start_date'], '%Y-%m-%d')
            update_data['start_date'] = sg_tz.localize(start_date)
        
        if 'end_date' in update_data and update_data['end_date']:
            end_date = datetime.strptime(update_data['end_date'], '%Y-%m-%d')
            # Set to start of day (12:00 AM) instead of end of day (11:59 PM)
            update_data['end_date'] = sg_tz.localize(end_date.replace(hour=0, minute=0, second=0))

        status_log_entries = None
        if 'status_log' in update_data and isinstance(update_data['status_log'], list) and update_data['status_log']:
            status_log_entries = update_data['status_log']
        update_data.pop('status_log', None)

        tasks_col = db.collection('Tasks')

        # Try to resolve by Firestore document id first
        doc_ref = tasks_col.document(task_id)
        doc = doc_ref.get()

        # If not found, try to resolve by business task_ID (and proj_ID if provided)
        if not doc.exists:
            query = tasks_col.where('task_ID', '==', task_id)
            # Narrow by proj_ID if available in payload
            proj_id = update_data.get('proj_ID')
            if proj_id:
                query = query.where('proj_ID', '==', proj_id)
            results = list(query.stream())
            if not results and proj_id:
                # fallback: try without proj filter in case payload proj_ID mismatches
                results = list(tasks_col.where('task_ID', '==', task_id).stream())
            if not results:
                return jsonify({'error': 'Task not found'}), 404
            doc_ref = results[0].reference

        # Get the OLD document data BEFORE updating (for notification comparison and permissions)
        old_doc = doc_ref.get()
        old_data = old_doc.to_dict() if old_doc.exists else {}
        old_assigned_to = old_data.get('assigned_to', []) if old_data else []
        old_owner_id = (old_data.get('owner_id') or old_data.get('owner')) if old_data else None

        owner_id_str = str(old_owner_id) if old_owner_id is not None else ''

        collaborator_ids = set()
        if isinstance(old_assigned_to, list):
            for entry in old_assigned_to:
                if entry is None:
                    continue
                if isinstance(entry, (str, int)):
                    collaborator_ids.add(str(entry))
                elif isinstance(entry, dict):
                    for key in ('id', 'user_id', 'userId'):
                        if entry.get(key) is not None:
                            collaborator_ids.add(str(entry[key]))
                            break

        is_owner = owner_id_str != '' and owner_id_str == current_user_id
        is_collaborator = current_user_id in collaborator_ids

        if not is_owner and not is_collaborator:
            return jsonify({'error': 'You do not have permission to update this task'}), 403

        allowed_fields_for_collaborators = {'task_desc', 'task_status', 'status_history', 'recurrence'}

        if is_owner:
            permitted_update = dict(update_data)
        else:
            permitted_update = {key: value for key, value in update_data.items() if key in allowed_fields_for_collaborators}
            print(f"🔒 Collaborator update permitted keys: {list(permitted_update.keys())}")

        project_end_limit = None
        project_identifier = (
            old_data.get('proj_ID')
            or old_data.get('proj_id')
            or update_data.get('proj_ID')
            or update_data.get('proj_id')
        )

        def parse_date_value(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value).date()
                except ValueError:
                    try:
                        return datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        return None
            return None

        try:
            if project_identifier:
                project_doc = db.collection('Projects').document(project_identifier).get()
                if project_doc.exists:
                    project_data = project_doc.to_dict() or {}
                    project_end_limit = _parse_date_value(project_data.get('end_date'))
        except Exception as resolve_error:
            print(f"⚠️ Failed to resolve project end date for task {task_id}: {resolve_error}")

        if project_end_limit is None:
            fallback_project_end = (
                old_data.get('proj_end_date')
                or old_data.get('project_end_date')
                or update_data.get('proj_end_date')
                or update_data.get('project_end_date')
            )
            project_end_limit = _parse_date_value(fallback_project_end)

        recurrence_payload = permitted_update.get('recurrence')
        if recurrence_payload is not None:
            if not isinstance(recurrence_payload, dict):
                return jsonify({'error': 'Invalid recurrence payload'}), 400

            normalized_recurrence = dict(recurrence_payload)
            normalized_recurrence['enabled'] = bool(normalized_recurrence.get('enabled'))

            if normalized_recurrence['enabled']:
                if 'end_condition' in normalized_recurrence:
                    normalized_recurrence['endCondition'] = normalized_recurrence.pop('end_condition')
                if 'end_date' in normalized_recurrence:
                    normalized_recurrence['endDate'] = normalized_recurrence.pop('end_date')
                if 'weekly_days' in normalized_recurrence and 'weeklyDays' not in normalized_recurrence:
                    normalized_recurrence['weeklyDays'] = normalized_recurrence.pop('weekly_days')
                if 'monthly_day' in normalized_recurrence and 'monthlyDay' not in normalized_recurrence:
                    normalized_recurrence['monthlyDay'] = normalized_recurrence.pop('monthly_day')
                if 'custom_unit' in normalized_recurrence and 'customUnit' not in normalized_recurrence:
                    normalized_recurrence['customUnit'] = normalized_recurrence.pop('custom_unit')
                if 'end_after_occurrences' in normalized_recurrence and 'endAfterOccurrences' not in normalized_recurrence:
                    normalized_recurrence['endAfterOccurrences'] = normalized_recurrence.pop('end_after_occurrences')

                frequency_value = normalized_recurrence.get('frequency')
                normalized_recurrence['frequency'] = str(frequency_value).lower() if frequency_value else ''

                allowed_frequencies = {'daily', 'weekly', 'monthly', 'custom'}
                if not normalized_recurrence['frequency']:
                    return jsonify({'error': 'Recurrence frequency is required when recurrence is enabled'}), 400
                if normalized_recurrence['frequency'] not in allowed_frequencies:
                    return jsonify({'error': f"Invalid recurrence frequency: {normalized_recurrence['frequency']}"}), 400

                try:
                    normalized_recurrence['interval'] = max(1, int(normalized_recurrence.get('interval') or 1))
                except (ValueError, TypeError):
                    normalized_recurrence['interval'] = 1

                if normalized_recurrence['frequency'] == 'weekly':
                    weekly_days = normalized_recurrence.get('weeklyDays') or []
                    if isinstance(weekly_days, list):
                        normalized_recurrence['weeklyDays'] = [str(day) for day in weekly_days if day]
                    else:
                        normalized_recurrence['weeklyDays'] = []
                else:
                    normalized_recurrence.pop('weeklyDays', None)

                if normalized_recurrence['frequency'] == 'monthly':
                    monthly_day = normalized_recurrence.get('monthlyDay')
                    if monthly_day in (None, '', 0):
                        normalized_recurrence['monthlyDay'] = None
                    else:
                        try:
                            normalized_recurrence['monthlyDay'] = int(monthly_day)
                        except (ValueError, TypeError):
                            return jsonify({'error': 'Invalid monthly recurrence configuration'}), 400
                else:
                    normalized_recurrence.pop('monthlyDay', None)

                if normalized_recurrence['frequency'] == 'custom':
                    normalized_recurrence['customUnit'] = normalized_recurrence.get('customUnit', 'days')
                else:
                    normalized_recurrence.pop('customUnit', None)

                end_condition_value = normalized_recurrence.get('endCondition') or 'never'
                end_condition_value = str(end_condition_value)
                if end_condition_value not in {'never', 'after', 'onDate'}:
                    end_condition_value = 'never'
                normalized_recurrence['endCondition'] = end_condition_value

                if end_condition_value == 'after':
                    try:
                        occurrences = int(normalized_recurrence.get('endAfterOccurrences') or 0)
                        if occurrences < 1:
                            raise ValueError
                        normalized_recurrence['endAfterOccurrences'] = occurrences
                    except (ValueError, TypeError):
                        return jsonify({'error': 'Recurrence endAfterOccurrences must be a positive number'}), 400
                    normalized_recurrence.pop('endDate', None)
                elif end_condition_value == 'onDate':
                    end_date_value = normalized_recurrence.get('endDate')
                    parsed_end = _parse_date_value(end_date_value)
                    if parsed_end is None:
                        return jsonify({'error': 'Invalid recurrence endDate'}), 400
                    if project_end_limit and parsed_end > project_end_limit:
                        parsed_end = project_end_limit
                    normalized_recurrence['endDate'] = parsed_end.isoformat()
                    normalized_recurrence.pop('endAfterOccurrences', None)
                else:
                    normalized_recurrence.pop('endDate', None)
                    normalized_recurrence.pop('endAfterOccurrences', None)

                permitted_update['recurrence'] = normalized_recurrence
            else:
                permitted_update['recurrence'] = {'enabled': False}

        series_id = old_data.get('recurrence_series_id') or (old_doc.id if old_doc and old_doc.exists else None)
        current_occurrence_index = old_data.get('recurrence_occurrence')
        if old_data.get('recurrence', {}).get('enabled'):
            if current_occurrence_index is None:
                current_occurrence_index = 1
        else:
            current_occurrence_index = None

        if recurrence_payload is not None:
            if permitted_update['recurrence'].get('enabled'):
                if current_occurrence_index is None:
                    current_occurrence_index = old_data.get('recurrence_occurrence') or 1
            else:
                current_occurrence_index = None

        if current_occurrence_index is not None:
            permitted_update['recurrence_occurrence'] = current_occurrence_index
        elif 'recurrence_occurrence' not in permitted_update:
            permitted_update['recurrence_occurrence'] = None

        if series_id:
            permitted_update['recurrence_series_id'] = series_id
        if 'recurrence_occurrence' in permitted_update and permitted_update['recurrence_occurrence'] == old_data.get('recurrence_occurrence'):
            permitted_update.pop('recurrence_occurrence')
        if 'recurrence_series_id' in permitted_update and permitted_update['recurrence_series_id'] == old_data.get('recurrence_series_id'):
            permitted_update.pop('recurrence_series_id')

        # Determine status change
        def normalize_status(value):
            if value in (None, '', 'None'):
                return 'Unassigned'
            return str(value)

        old_status_value = old_data.get('task_status') if old_data else None
        old_status_normalized = normalize_status(old_status_value)
        new_status_value = permitted_update.get('task_status') if 'task_status' in permitted_update else old_status_value
        new_status_normalized = normalize_status(new_status_value)
        status_changed = 'task_status' in permitted_update and new_status_normalized != old_status_normalized

        # Resolve staff display name
        user_display_name = current_user_name
        if not user_display_name:
            try:
                user_doc = db.collection('Users').document(current_user_id).get()
                if user_doc.exists:
                    user_display_name = user_doc.to_dict().get('name', '') or ''
            except Exception:
                user_display_name = ''
        if not user_display_name:
            user_display_name = 'Unknown User'

        status_log_entries_to_append = []
        change_log_entry = None

        if status_log_entries:
            try:
                first_entry = status_log_entries[0]
                change_log_entry = {
                    'timestamp': first_entry.get('timestamp') or datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
                    'old_status': first_entry.get('old_status', old_status_normalized),
                    'new_status': first_entry.get('new_status', new_status_normalized),
                    'staff_name': first_entry.get('staff_name', user_display_name),
                    'changed_by': first_entry.get('changed_by', current_user_id)
                }
                status_log_entries_to_append.append(change_log_entry)
            except Exception:
                status_log_entries_to_append = []
                change_log_entry = None

        if status_changed and change_log_entry is None:
            change_log_entry = {
                'timestamp': datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
                'old_status': old_status_normalized,
                'new_status': new_status_normalized,
                'staff_name': user_display_name,
                'changed_by': current_user_id
            }
            status_log_entries_to_append.append(change_log_entry)

        if change_log_entry and 'status_history' not in permitted_update:
            existing_history = old_data.get('status_history') if old_data else []
            if existing_history is None:
                existing_history = []
            permitted_update['status_history'] = [*existing_history, change_log_entry]

        if not permitted_update and not status_log_entries_to_append:
            return jsonify({'error': 'No permitted fields to update'}), 400

        permitted_update['updatedAt'] = firestore.SERVER_TIMESTAMP
        status_log_update = firestore.ArrayUnion(status_log_entries_to_append) if status_log_entries_to_append else None

        # Apply the update
        if permitted_update:
            doc_ref.update(permitted_update)
        if status_log_update is not None:
            doc_ref.update({'status_log': status_log_update})

        # Get updated document for response
        updated_doc = doc_ref.get()
        if updated_doc.exists:
            raw_updated_data = updated_doc.to_dict() or {}
            response_data = dict(raw_updated_data)
            response_data['id'] = updated_doc.id
            
            # Convert timestamps for response
            if 'start_date' in response_data and response_data['start_date']:
                response_data['start_date'] = response_data['start_date'].isoformat()
            if 'end_date' in response_data and response_data['end_date']:
                response_data['end_date'] = response_data['end_date'].isoformat()
            if 'updatedAt' in response_data and response_data['updatedAt']:
                response_data['updatedAt'] = response_data['updatedAt'].isoformat()
            if 'createdAt' in response_data and response_data['createdAt']:
                response_data['createdAt'] = response_data['createdAt'].isoformat()

            # ================== SEND EMAILS FOR OWNER CHANGE ==================
            try:
                # Check both 'owner_id' and 'owner' fields (depending on your frontend)
                new_owner_id = update_data.get('owner_id') or update_data.get('owner')
                
                print(f"🔍 EMAIL CHECK - Raw update_data: {update_data}")
                print(f"🔍 EMAIL CHECK - update_data.get('owner'): {update_data.get('owner')}")
                print(f"🔍 EMAIL CHECK - update_data.get('owner_id'): {update_data.get('owner_id')}")
                print(f"🔍 EMAIL CHECK - new_owner_id (final): {new_owner_id}")
                print(f"🔍 EMAIL CHECK - old_owner_id from old_doc: {old_owner_id}")
                print(f"🔍 EMAIL CHECK - Are they different? {old_owner_id != new_owner_id}")
                print(f"🔍 EMAIL CHECK - Is new_owner_id truthy? {bool(new_owner_id)}")
                
                # Check if owner has changed
                if new_owner_id and old_owner_id != new_owner_id:
                    print(f"👤 OWNER CHANGE DETECTED: {old_owner_id} → {new_owner_id}")
                    from services.email_service import email_service
                    
                    # Get new owner's info
                    print(f"📧 Fetching new owner data for: {new_owner_id}")
                    new_owner_doc = db.collection('Users').document(new_owner_id).get()
                    
                    if new_owner_doc.exists:
                        new_owner_data = new_owner_doc.to_dict()
                        new_owner_email = new_owner_data.get('email')
                        new_owner_name = new_owner_data.get('name', 'User')
                        print(f"✅ New owner found: {new_owner_name} ({new_owner_email})")
                        
                        # Get old owner's info (for CC)
                        old_owner_email = None
                        old_owner_name = 'Previous Owner'
                        if old_owner_id:
                            print(f"📧 Fetching old owner data for: {old_owner_id}")
                            old_owner_doc = db.collection('Users').document(old_owner_id).get()
                            if old_owner_doc.exists:
                                old_owner_data = old_owner_doc.to_dict()
                                old_owner_email = old_owner_data.get('email')
                                old_owner_name = old_owner_data.get('name', 'Previous Owner')
                                print(f"✅ Old owner found: {old_owner_name} ({old_owner_email})")
                        
                        # Prepare task details for email
                        task_name = response_data.get('task_name', 'Unknown Task')
                        task_desc = response_data.get('task_desc', '')
                        project_name = response_data.get('proj_name', '')
                        
                        # Get who made the transfer (from request context or use new owner as fallback)
                        transferred_by_name = new_owner_name  # You can enhance this with actual user context
                        
                        # Format dates safely
                        start_date_str = 'Not specified'
                        end_date_str = None
                        
                        if 'start_date' in response_data and response_data['start_date']:
                            try:
                                start_date_str = datetime.fromisoformat(response_data['start_date']).strftime('%Y-%m-%d')
                            except:
                                start_date_str = str(response_data['start_date'])[:10]
                        
                        if 'end_date' in response_data and response_data['end_date']:
                            try:
                                end_date_str = datetime.fromisoformat(response_data['end_date']).strftime('%Y-%m-%d')
                            except:
                                end_date_str = str(response_data['end_date'])[:10]
                        
                        print("📧 Preparing to send ownership transfer email...")
                        print(f"   To: {new_owner_email}")
                        print(f"   CC: {old_owner_email}")
                        print(f"   Task: {task_name}")
                        
                        # Send email to new owner (with old owner CC'd)
                        if new_owner_email:
                            success = email_service.send_task_transfer_ownership_email(
                                new_owner_email=new_owner_email,
                                new_owner_name=new_owner_name,
                                old_owner_email=old_owner_email if old_owner_email else '',
                                old_owner_name=old_owner_name,
                                task_name=task_name,
                                task_desc=task_desc,
                                project_name=project_name,
                                transferred_by_name=transferred_by_name,
                                start_date=start_date_str,
                                end_date=end_date_str
                            )
                            if success:
                                print(f"✅ OWNERSHIP TRANSFER EMAIL SENT to {new_owner_email} (CC: {old_owner_email})")
                            else:
                                print("❌ FAILED to send ownership transfer email")
                        else:
                            print(f"⚠️ No email found for new owner {new_owner_id}")
                    else:
                        print(f"⚠️ New owner document not found: {new_owner_id}")
                else:
                    print(f"⏭️  No owner change detected (both are {new_owner_id})")
                        
            except Exception as e:
                print(f"❌ Failed to send owner change email: {e}")
                import traceback
                traceback.print_exc()

            # ================== CREATE NOTIFICATIONS FOR TASK UPDATES ==================
            try:
                print("🔔 NOTIFICATION BLOCK REACHED")
                
                # Get the NEW assigned_to list (after update)
                # old_assigned_to was captured before the update above
                new_assigned_to = response_data.get('assigned_to', [])
                
                # Determine what ACTUALLY changed by comparing old vs new values
                # Exclude only true metadata/system fields
                metadata_fields = ['updatedAt', 'createdAt', 'status_log', 'id', 'task_ID', 'proj_ID']
                old_values_dict = old_doc.to_dict() if old_doc.exists else {}
                
                actually_changed = []
                for key in update_data.keys():
                    if key in metadata_fields:
                        continue
                    
                    old_val = old_values_dict.get(key)
                    new_val = update_data.get(key)
                    
                    # Compare values (handle different types)
                    if key == 'assigned_to':
                        # For lists, sort and compare
                        old_sorted = sorted(old_val) if old_val else []
                        new_sorted = sorted(new_val) if new_val else []
                        if old_sorted != new_sorted:
                            actually_changed.append(key)
                            print(f"   ✓ {key} changed: {old_sorted} → {new_sorted}")
                    elif key in ['start_date', 'end_date']:
                        # For dates, compare the calendar date only (ignore time and timezone)
                        old_date = old_val.date() if old_val and hasattr(old_val, 'date') else None
                        new_date = new_val.date() if new_val and hasattr(new_val, 'date') else None
                        
                        if old_date != new_date:
                            actually_changed.append(key)
                            print(f"   ✓ {key} changed: {old_date} → {new_date}")
                    elif old_val != new_val:
                        actually_changed.append(key)
                        print(f"   ✓ {key} changed: '{old_val}' (type: {type(old_val).__name__}) → '{new_val}' (type: {type(new_val).__name__})")
                
                updated_fields = actually_changed
                assignment_changed = 'assigned_to' in updated_fields
                other_fields_changed = [f for f in updated_fields if f != 'assigned_to']
                
                print(f"   All update_data keys: {list(update_data.keys())}")
                print(f"   Actually changed fields: {updated_fields}")
                print(f"   Assignment changed: {assignment_changed}")
                print(f"   Other fields changed: {other_fields_changed}")
                print(f"   Old assigned_to: {old_assigned_to}")
                print(f"   New assigned_to: {new_assigned_to}")
                
                notification_task_data = {
                    'task_name': response_data.get('task_name', 'Unknown Task'),
                    'task_ID': response_data.get('task_ID'),
                    'id': updated_doc.id,
                    'proj_ID': response_data.get('proj_ID')
                }
                
                # Prepare old and new values for changed fields
                old_values = old_doc.to_dict() if old_doc.exists else {}
                new_values = response_data
                
                # SCENARIO 1: Assignment changed - notify NEWLY added users about assignment
                if assignment_changed and new_assigned_to:
                    newly_assigned = [user for user in new_assigned_to if user not in old_assigned_to]
                    already_assigned = [user for user in new_assigned_to if user in old_assigned_to]
                    
                    # Notify newly assigned users
                    if newly_assigned:
                        print(f"🎯 Notifying {len(newly_assigned)} NEWLY assigned users")
                        notification_service.notify_task_assigned(notification_task_data, newly_assigned)
                        print(f"✅ Task assignment notifications sent to: {newly_assigned}")
                    
                    # If other fields also changed, notify already assigned users about updates
                    if other_fields_changed and already_assigned:
                        print(f"🎯 Notifying {len(already_assigned)} ALREADY assigned users about updates")
                        notification_service.notify_task_updated(notification_task_data, already_assigned, other_fields_changed, old_values, new_values)
                        print(f"✅ Task update notifications sent to: {already_assigned}")
                
                # SCENARIO 2: Other fields changed WITHOUT assignment change - notify ALL current assignees
                elif other_fields_changed and new_assigned_to:
                    print(f"🎯 Notifying {len(new_assigned_to)} users about task details update (no assignment change)")
                    notification_service.notify_task_updated(notification_task_data, new_assigned_to, other_fields_changed, old_values, new_values)
                    print("✅ Task update notifications sent")
                else:
                    print("⏭️  No notifications needed (no changes or no assignees)")
                
            except Exception as e:
                print(f"❌ Failed to create update notifications: {e}")
                import traceback
                traceback.print_exc()

            try:
                next_instance_payload = None
                recurrence_info = raw_updated_data.get('recurrence') or {}
                series_id = raw_updated_data.get('recurrence_series_id') or updated_doc.id
                current_occurrence_index = raw_updated_data.get('recurrence_occurrence')
                if recurrence_info.get('enabled'):
                    if current_occurrence_index is None:
                        current_occurrence_index = 1
                else:
                    current_occurrence_index = None

                if (
                    status_changed
                    and new_status_normalized.lower() == 'completed'
                    and recurrence_info.get('enabled')
                    and current_occurrence_index is not None
                ):
                    current_start_dt = raw_updated_data.get('start_date')
                    current_end_dt = raw_updated_data.get('end_date')
                    if isinstance(current_start_dt, str):
                        try:
                            current_start_dt = datetime.fromisoformat(current_start_dt)
                        except Exception:
                            current_start_dt = None
                    if isinstance(current_end_dt, str):
                        try:
                            current_end_dt = datetime.fromisoformat(current_end_dt)
                        except Exception:
                            current_end_dt = None

                    next_start_dt, next_end_dt = _compute_next_occurrence_dates(current_start_dt, current_end_dt, recurrence_info)
                    if next_start_dt:
                        next_occurrence_index = (current_occurrence_index or 1) + 1
                        if not _should_stop_recurrence(recurrence_info, next_occurrence_index, next_start_dt):
                            recurrence_clone = dict(recurrence_info)
                            new_task_data = {
                                'proj_name': raw_updated_data.get('proj_name', ''),
                                'proj_ID': raw_updated_data.get('proj_ID'),
                                'task_name': raw_updated_data.get('task_name', ''),
                                'task_desc': raw_updated_data.get('task_desc', ''),
                                'start_date': next_start_dt,
                                'end_date': next_end_dt,
                                'owner': raw_updated_data.get('owner'),
                                'assigned_to': raw_updated_data.get('assigned_to', []) or [],
                                'attachments': raw_updated_data.get('attachments', []),
                                'task_status': 'Unassigned',
                                'priority_level': raw_updated_data.get('priority_level'),
                                'hasSubtasks': raw_updated_data.get('hasSubtasks', False),
                                'is_deleted': False,
                                'recurrence': recurrence_clone,
                                'recurrence_occurrence': next_occurrence_index,
                                'recurrence_series_id': series_id,
                                'status_history': [],
                                'status_log': [],
                                'createdAt': firestore.SERVER_TIMESTAMP,
                                'updatedAt': firestore.SERVER_TIMESTAMP
                            }

                            new_doc_ref = db.collection('Tasks').add(new_task_data)
                            new_doc = new_doc_ref[1]
                            new_doc_id = new_doc.id
                            try:
                                new_doc.update({'recurrence_series_id': series_id})
                            except Exception:
                                pass

                            assigned_users_next = new_task_data.get('assigned_to') or []
                            if assigned_users_next:
                                try:
                                    notification_service.notify_task_assigned(
                                        {
                                            'task_name': new_task_data.get('task_name', 'Unknown Task'),
                                            'task_ID': new_task_data.get('task_ID'),
                                            'id': new_doc_id,
                                            'proj_ID': new_task_data.get('proj_ID')
                                        },
                                        assigned_users_next
                                    )
                                except Exception as notify_error:
                                    print(f"⚠️ Failed to notify new recurring assignees: {notify_error}")

                            next_instance_payload = dict(new_task_data)
                            next_instance_payload['id'] = new_doc_id
                            next_instance_payload['start_date'] = next_start_dt.isoformat()
                            if next_end_dt:
                                next_instance_payload['end_date'] = next_end_dt.isoformat()
                            else:
                                next_instance_payload['end_date'] = None
                            next_instance_payload.pop('createdAt', None)
                            next_instance_payload.pop('updatedAt', None)
                            next_instance_payload['task_status'] = 'Unassigned'
                            next_instance_payload['recurrence_occurrence'] = next_occurrence_index
                            next_instance_payload['recurrence_series_id'] = series_id
                            response_data['next_instance'] = next_instance_payload
                            response_data['recurrence_series_id'] = series_id

                            response_data['recurrence_occurrence'] = current_occurrence_index
                            try:
                                doc_ref.update({
                                    'recurrence_occurrence': current_occurrence_index,
                                    'recurrence_series_id': series_id
                                })
                            except Exception:
                                pass
            except Exception as recurrence_error:
                print(f"⚠️ Failed to generate next recurring instance: {recurrence_error}")

            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Task not found after update'}), 404

    except ValueError as e:
        return jsonify({'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== DELETE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists before deleting
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404
        
        # Delete document
        doc_ref.delete()

        return jsonify({'message': 'Task deleted successfully', 'id': task_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== GET TASKS BY PROJECT ID ===============
@tasks_bp.route('/api/projects/<proj_id>/tasks', methods=['GET'])
def get_tasks_by_project(proj_id):
    try:
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        # Query tasks by project ID
        query = tasks_ref.where('proj_ID', '==', proj_id)
        tasks = query.stream()
        
        task_list = []
        for task in tasks:
            task_data = task.to_dict()
            task_data['id'] = task.id
            
            # Convert timestamps to ISO format
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()
            
            task_list.append(task_data)
            
        return jsonify(task_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== GET ALL USERS FOR DROPDOWN ===============
@tasks_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        db = get_firestore_client()
        users_ref = db.collection('Users')  # Adjust collection name as needed
        users = users_ref.stream()
        
        user_list = []
        for user in users:
            user_data = user.to_dict()
            # Only return necessary fields for dropdown
            user_info = {
                'id': user.id,
                'name': user_data.get('name', ''),
                'email': user_data.get('email', '')  # Optional: include email for better identification
            }
            user_list.append(user_info)
        
        # Sort users by name for better UX
        user_list.sort(key=lambda x: x['name'].lower())
        
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# =============== GET ALL PROJECTS FOR DROPDOWN ===============
# @tasks_bp.route('/api/projects', methods=['GET'])
# def get_all_projects():
#     try:
#         db = get_firestore_client()
#         projects_ref = db.collection('Projects')  # Adjust collection name as needed
#         projects = projects_ref.stream()
        
#         project_list = []
#         for project in projects:
#             project_data = project.to_dict()
#             # Only return necessary fields for dropdown
#             project_info = {
#                 'id': project.id,
#                 'proj_id': project_data.get('proj_ID', project.id),  # Use proj_id field
#                 'name': project_data.get('name', '') or project_data.get('project_name', ''),  # Adjust field name
#                 'description': project_data.get('description', '')  # Optional
#             }
#             project_list.append(project_info)
        
#         # Sort projects by name for better UX
#         project_list.sort(key=lambda x: x['name'].lower() if x['name'] else '')
        
#         return jsonify(project_list), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
@tasks_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    try:
        db = get_firestore_client()
        projects_ref = db.collection('Projects')  # Make sure this collection name is correct
        projects = projects_ref.stream()
        
        project_list = []
        for project in projects:
            project_data = project.to_dict()
            print(f"Project document ID: {project.id}")
            print(f"Project data: {project_data}")
            
            # Be very defensive about field access
            project_info = {
                'id': project.id,
                'proj_ID': project_data.get('proj_ID') or project_data.get('proj_id') or project.id,
                'name': project_data.get('name') or project_data.get('project_name') or f'Project {project.id}',
                'description': project_data.get('description') or ''
            }
            
            print(f"Processed project_info: {project_info}")
            project_list.append(project_info)
        
        print(f"Final project_list: {project_list}")
        return jsonify(project_list), 200
    except Exception as e:
        print(f"Error in get_all_projects: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/tasks/<task_id>/delete', methods=['PUT'])
def soft_delete_task(task_id):
    try:
        print(f"🗑️ CASCADE DELETE for task: {task_id}", flush=True)
        
        db = get_firestore_client()
        deleted_at = firestore.SERVER_TIMESTAMP
        
        # Get user validation
        request_data = request.get_json()
        user_id = request_data.get('userId') if request_data else None
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Validate task ownership
        task_ref = db.collection('Tasks').document(task_id)
        task_doc = task_ref.get()
        
        if not task_doc.exists:
            return jsonify({'error': 'Task not found'}), 404
            
        task_data = task_doc.to_dict()
        
        # 🔍 DEBUG: Print ALL task fields to find the correct name field
        print(f"🔍 DEBUG: ALL task fields: {list(task_data.keys())}", flush=True)
        print(f"🔍 DEBUG: Full task data: {task_data}", flush=True)
        
        # 🔍 DEBUG: Test different possible field names
        taskname_field = task_data.get('taskname')
        task_name_field = task_data.get('task_name') 
        name_field = task_data.get('name')
        title_field = task_data.get('title')
        
        print(f"🔍 DEBUG: taskname = '{taskname_field}'", flush=True)
        print(f"🔍 DEBUG: task_name = '{task_name_field}'", flush=True)
        print(f"🔍 DEBUG: name = '{name_field}'", flush=True)
        print(f"🔍 DEBUG: title = '{title_field}'", flush=True)
        
        if str(task_data.get('owner', '')) != str(user_id):
            return jsonify({'error': 'Only task owner can delete this task'}), 403
        
        # Delete the task
        task_ref.update({
            'is_deleted': True,
            'deleted_at': deleted_at
        })
        print(f"✅ Task {task_id} soft deleted", flush=True)
        
        # Find and cascade delete subtasks
        subtasks_ref = db.collection('subtasks')  # LOWERCASE
        subtasks_query = subtasks_ref.where('parent_task_id', '==', task_id)
        subtasks = list(subtasks_query.stream())
        
        deleted_count = 0
        for subtask_doc in subtasks:
            subtask_data = subtask_doc.to_dict()
            
            if not subtask_data.get('is_deleted', False):
                subtask_ref = db.collection('subtasks').document(subtask_doc.id)
                subtask_ref.update({
                    'is_deleted': True,
                    'deleted_at': deleted_at,
                    'deleted_by_cascade': True,
                    'cascade_parent_id': task_id
                })
                deleted_count += 1
                print(f"✅ Subtask {subtask_doc.id} cascade deleted", flush=True)
        
        print(f"🎉 CASCADE COMPLETE: {deleted_count} subtasks deleted", flush=True)
        
        # Try multiple field names for task name (with proper fallback)
        final_task_name = (
            taskname_field or 
            task_name_field or 
            name_field or 
            title_field or 
            'Unknown Task'
        )
        
        print(f"🔍 DEBUG: Final task name will be: '{final_task_name}'", flush=True)
        
        return jsonify({
            'message': f'Task and {deleted_count} subtasks moved to trash',
            'task_id': task_id,
            'deleted_subtasks_count': deleted_count,
            'task_name': final_task_name  # Use the debugged name
        }), 200
        
    except Exception as e:
        print(f"💥 CASCADE ERROR: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@tasks_bp.route('/api/test/update-subtask/<subtask_id>', methods=['PUT'])
def test_update_subtask(subtask_id):
    try:
        db = get_firestore_client()
        
        print(f"🧪 TEST: Attempting to update subtask {subtask_id}", flush=True)
        
        # Get the subtask first
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            print(f"❌ TEST: Subtask {subtask_id} not found", flush=True)
            return jsonify({'error': 'Subtask not found'}), 404
        
        current_data = subtask_doc.to_dict()
        print(f"📋 TEST: Current subtask data: is_deleted = {current_data.get('is_deleted')}", flush=True)
        
        # Try to update it
        print(f"🔄 TEST: Updating subtask...", flush=True)
        subtask_ref.update({
            'is_deleted': True,
            'test_field': 'updated_by_test'
        })
        
        # Verify the update
        updated_doc = subtask_ref.get()
        updated_data = updated_doc.to_dict()
        
        print(f"✅ TEST: Update result: is_deleted = {updated_data.get('is_deleted')}", flush=True)
        print(f"✅ TEST: Test field = {updated_data.get('test_field')}", flush=True)
        
        return jsonify({
            'message': 'Test update successful',
            'before': current_data.get('is_deleted'),
            'after': updated_data.get('is_deleted'),
            'test_field': updated_data.get('test_field')
        }), 200
        
    except Exception as e:
        print(f"💥 TEST ERROR: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/debug/task/<task_id>/subtasks', methods=['GET'])
def debug_subtasks(task_id):
    try:
        db = get_firestore_client()
        
        print(f"🔍 DEBUG: Looking for ALL subtasks for task {task_id}", flush=True)
        
        # Query ALL subtasks (including deleted ones)
        subtasks_ref = db.collection('subtasks')
        all_query = subtasks_ref.where('parent_task_id', '==', task_id)
        all_docs = all_query.stream()
        
        results = []
        for doc in all_docs:
            data = doc.to_dict()
            results.append({
                'id': doc.id,
                'name': data.get('name', data.get('subtask_name', 'Unknown')),
                'is_deleted': data.get('is_deleted', False),
                'deleted_at': data.get('deleted_at'),
                'parent_task_id': data.get('parent_task_id')
            })
            
            print(f"   📋 Subtask {doc.id}: is_deleted={data.get('is_deleted')}, name={data.get('name')}", flush=True)
        
        return jsonify({
            'task_id': task_id,
            'total_subtasks': len(results),
            'subtasks': results
        }), 200
        
    except Exception as e:
        print(f"💥 DEBUG ERROR: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

    
# =============== GET DELETED TASKS ===============
@tasks_bp.route('/api/tasks/deleted', methods=['GET'])
def get_deleted_tasks():
    """Get all deleted tasks (where is_deleted = True)"""
    try:
        print("📋 === GET DELETED TASKS ===")
        
        db = get_firestore_client()
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        
        # Query for deleted tasks where user is owner or assigned
        tasks_ref = db.collection('Tasks')
        query = tasks_ref.where('is_deleted', '==', True)
        
        tasks = []
        seen_ids = set()
        
        # Get tasks where user is assigned
        try:
            assigned_query = query.where('assignedto', 'array_contains', user_id)
            for doc in assigned_query.stream():
                if doc.id not in seen_ids:
                    task_data = doc.to_dict()
                    task_data['id'] = doc.id
                    
                    # Convert timestamps to ISO format
                    if 'deleted_at' in task_data and task_data['deleted_at']:
                        task_data['deleted_at'] = task_data['deleted_at'].isoformat()
                    if 'startdate' in task_data and task_data['startdate']:
                        task_data['startdate'] = task_data['startdate'].isoformat()
                    if 'enddate' in task_data and task_data['enddate']:
                        task_data['enddate'] = task_data['enddate'].isoformat()
                    
                    tasks.append(task_data)
                    seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying assigned tasks: {e}")
        
        # Get tasks where user is owner
        try:
            owner_query = query.where('owner', '==', user_id)
            for doc in owner_query.stream():
                if doc.id not in seen_ids:
                    task_data = doc.to_dict()
                    task_data['id'] = doc.id
                    
                    # Convert timestamps to ISO format
                    if 'deleted_at' in task_data and task_data['deleted_at']:
                        task_data['deleted_at'] = task_data['deleted_at'].isoformat()
                    if 'startdate' in task_data and task_data['startdate']:
                        task_data['startdate'] = task_data['startdate'].isoformat()
                    if 'enddate' in task_data and task_data['enddate']:
                        task_data['enddate'] = task_data['enddate'].isoformat()
                    
                    tasks.append(task_data)
                    seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying owned tasks: {e}")
        
        print(f"📊 Found {len(tasks)} deleted tasks for user {user_id}")
        return jsonify(tasks), 200
        
    except Exception as e:
        print(f"❌ Error fetching deleted tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== GET DELETED SUBTASKS ===============
@tasks_bp.route('/api/subtasks/deleted', methods=['GET']) 
def get_deleted_subtasks():
    try:
        print("🔍 GET DELETED SUBTASKS API CALLED", flush=True)
        db = get_firestore_client()
        
        user_id = request.args.get('userId')
        print(f"   User ID: {user_id}", flush=True)
        
        if not user_id:
            return jsonify({'error': 'userId parameter is required'}), 400
        
        # Query ALL deleted subtasks (no owner filter for cascade deleted ones)
        subtasks_ref = db.collection('subtasks')  # LOWERCASE
        query = subtasks_ref.where('is_deleted', '==', True)  # ONLY filter by is_deleted
        
        subtasks = []
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            
            # Include subtasks that are either:
            # 1. Owned by the user, OR
            # 2. Cascade deleted from tasks owned by the user
            include_subtask = False
            
            # Check if user owns the subtask directly
            if data.get('owner') == user_id:
                include_subtask = True
                print(f"   Found user-owned deleted subtask: {doc.id}", flush=True)
            
            # Check if it's cascade deleted from user's task
            elif data.get('deleted_by_cascade', False):
                cascade_parent_id = data.get('cascade_parent_id')
                if cascade_parent_id:
                    # Check if the parent task belongs to this user
                    parent_task_ref = db.collection('Tasks').document(cascade_parent_id)
                    parent_task = parent_task_ref.get()
                    if parent_task.exists:
                        parent_data = parent_task.to_dict()
                        if str(parent_data.get('owner', '')) == str(user_id):
                            include_subtask = True
                            print(f"   Found cascade deleted subtask: {doc.id} (from task {cascade_parent_id})", flush=True)
            
            if include_subtask:
                subtask_info = {
                    'id': doc.id,
                    'name': data.get('name', 'Unknown Subtask'),
                    'subtaskname': data.get('name', 'Unknown Subtask'),
                    'description': data.get('description', ''),
                    'subtaskdescription': data.get('description', ''),
                    'is_deleted': data.get('is_deleted', False),
                    'deleted_at': data.get('deleted_at'),
                    'parent_task_id': data.get('parent_task_id'),
                    'deleted_by_cascade': data.get('deleted_by_cascade', False),
                    'cascade_parent_id': data.get('cascade_parent_id')
                }
                
                # Convert timestamp
                if subtask_info['deleted_at']:
                    try:
                        subtask_info['deleted_at'] = subtask_info['deleted_at'].isoformat()
                    except:
                        pass
                
                subtasks.append(subtask_info)
        
        print(f"📊 Returning {len(subtasks)} deleted subtasks for user", flush=True)
        return jsonify(subtasks), 200
        
    except Exception as e:
        print(f"💥 Error getting deleted subtasks: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== RESTORE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>/restore', methods=['PUT'])
def restore_task(task_id):
    """
    Restore a soft-deleted task by setting is_deleted = False
    """
    try:
        print(f"🔄 Restoring task: {task_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Task {task_id} not found")
            return jsonify({'error': 'Task not found'}), 404
        
        # Get current task data
        task_data = doc.to_dict()
        
        # Check if task is actually deleted
        if not task_data.get('is_deleted', False):
            return jsonify({'error': 'Task is not deleted'}), 400
        
        print(f"📝 Restoring task: {task_data.get('taskname', 'Unknown')}")
        
        # RESTORE: Set is_deleted back to False
        update_data = {
            'is_deleted': False,
            'deleted_at': None,  # Clear the deleted timestamp
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.update(update_data)
        print(f"✅ Task {task_id} restored successfully")
        
        return jsonify({
            "message": "Task restored successfully",
            "task_id": task_id,
            "is_deleted": False,
            "task_name": task_data.get('taskname', 'Unknown Task')
        }), 200
        
    except Exception as e:
        print(f"❌ Error restoring task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== RESTORE SUBTASK ===============
@tasks_bp.route('/api/subtasks/<subtask_id>/restore', methods=['PUT'])
def restore_subtask(subtask_id):
    """
    Restore a soft-deleted subtask by setting is_deleted = False
    """
    try:
        print(f"🔄 Restoring subtask: {subtask_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('subtasks').document(subtask_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Subtask {subtask_id} not found")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Get current subtask data
        subtask_data = doc.to_dict()
        
        # Check if subtask is actually deleted
        if not subtask_data.get('is_deleted', False):
            return jsonify({'error': 'Subtask is not deleted'}), 400
        
        print(f"📝 Restoring subtask: {subtask_data.get('subtaskname', 'Unknown')}")
        
        # RESTORE: Set is_deleted back to False
        update_data = {
            'is_deleted': False,
            'deleted_at': None,  # Clear the deleted timestamp
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.update(update_data)
        print(f"✅ Subtask {subtask_id} restored successfully")
        
        return jsonify({
            "message": "Subtask restored successfully",
            "subtask_id": subtask_id,
            "is_deleted": False,
            "subtask_name": subtask_data.get('subtaskname', 'Unknown Subtask')
        }), 200
        
    except Exception as e:
        print(f"❌ Error restoring subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== PERMANENTLY DELETE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>/permanent', methods=['DELETE'])
def permanently_delete_task(task_id):
    """
    Permanently delete a task (actually remove from database)
    """
    try:
        print(f"💥 Permanently deleting task: {task_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Task {task_id} not found")
            return jsonify({'error': 'Task not found'}), 404
        
        # Get current task data for logging
        task_data = doc.to_dict()
        print(f"💥 Permanently deleting task: {task_data.get('taskname', 'Unknown')}")
        
        # HARD DELETE: Actually remove the document
        doc_ref.delete()
        print(f"✅ Task {task_id} permanently deleted")
        
        return jsonify({
            "message": "Task permanently deleted",
            "task_id": task_id
        }), 200
        
    except Exception as e:
        print(f"❌ Error permanently deleting task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== PERMANENTLY DELETE SUBTASK ===============
@tasks_bp.route('/api/subtasks/<subtask_id>/permanent', methods=['DELETE'])
def permanently_delete_subtask(subtask_id):
    """
    Permanently delete a subtask (actually remove from database)
    """
    try:
        print(f"💥 Permanently deleting subtask: {subtask_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('subtasks').document(subtask_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Subtask {subtask_id} not found")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Get current subtask data for logging
        subtask_data = doc.to_dict()
        print(f"💥 Permanently deleting subtask: {subtask_data.get('subtaskname', 'Unknown')}")
        
        # HARD DELETE: Actually remove the document
        doc_ref.delete()
        print(f"✅ Subtask {subtask_id} permanently deleted")
        
        return jsonify({
            "message": "Subtask permanently deleted",
            "subtask_id": subtask_id
        }), 200
        
    except Exception as e:
        print(f"❌ Error permanently deleting subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

