<template>
  <div class="transfer-ownership-wrapper">
    <!-- Transfer Ownership Modal -->
    <div v-if="visible" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Transfer {{ isSubtask ? 'Subtask' : 'Task' }} Ownership</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="transfer-form">
            <div class="current-owner-info">
              <h4>Current Owner</h4>
              <div class="user-info">
                <div class="user-avatar creator">
                  {{ getInitials(currentOwnerName) }}
                </div>
                <div class="user-details">
                  <p class="user-name">{{ currentOwnerName }}</p>
                  <p class="user-role">Current Owner</p>
                </div>
              </div>
            </div>

            <div class="new-owner-selection">
              <h4>Select New Owner</h4>
              <div v-if="transferEligibleUsers.length === 0" class="no-eligible-users">
                <p>No eligible users found for ownership transfer.</p>
                <p class="explanation">{{ getTransferRestrictionExplanation() }}</p>
              </div>
              <div v-else class="user-selection-list">
                <div 
                  v-for="user in transferEligibleUsers" 
                  :key="user.id" 
                  class="user-selection-item"
                  :class="{ selected: selectedNewOwner === user.id }"
                  @click="selectUser(user.id)"
                >
                  <div class="user-avatar assignee">
                    {{ getInitials(user.name) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ user.name }}</p>
                    <p class="user-role">{{ user.department }}</p>
                  </div>
                  <div class="selection-indicator">
                    {{ selectedNewOwner === user.id ? '✓' : '' }}
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-actions">
              <button @click="closeModal" class="cancel-btn">Cancel</button>
              <button 
                @click="showTransferConfirmation" 
                class="transfer-btn"
                :disabled="!selectedNewOwner || transferring">
                {{ transferring ? 'Transferring...' : 'Transfer Ownership' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmationModal" class="modal-overlay" @click="cancelConfirmation">
      <div class="modal-content confirmation-modal" @click.stop>
        <div class="modal-header">
          <h3>⚠️ Confirm Transfer</h3>
        </div>
        <div class="modal-body">
          <p class="confirmation-text">
            Are you sure you want to transfer ownership to 
            <strong>{{ transferEligibleUsers.find(u => u.id === selectedNewOwner)?.name }}</strong>?
          </p>
          <p class="warning-text">
            Once ownership is transferred, you cannot revert this change.
          </p>
          
          <div class="modal-actions">
            <button @click="cancelConfirmation" class="cancel-btn">
              Cancel
            </button>
            <button @click="confirmTransferOwnership" class="confirm-btn">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { taskService } from '../services/taskService.js'

export default {
  name: 'TransferOwnership',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    task: {
      type: Object,
      required: true
    },
    users: {
      type: Array,
      required: true
    },
    taskCollaborators: {
      type: Array,
      required: true
    },
    isSubtask: {
    type: Boolean,
    default: false
    } 
  },
  data() {
    return {
      selectedNewOwner: null,
      transferring: false,
      transferEligibleUsers: [],
      showConfirmationModal: false,
    }
  },
  computed: {
    currentOwnerName() {
      const owner = this.users.find(u => String(u.id) === String(this.task.owner));
      return owner ? owner.name : 'Unknown User';
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadTransferEligibleUsers();
      } else {
        this.resetComponent();
      }
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },

    resetComponent() {
      this.selectedNewOwner = null;
      this.transferring = false;
      this.transferEligibleUsers = [];
      this.showConfirmationModal = false;
    },

    getInitials(name) {
      if (!name) return 'U';
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
    },

    // Check if current user can transfer ownership
    canTransferOwnership() {
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
      
      // Check if user is the owner AND has manager role (role_num = 3)
      return String(this.task.owner) === String(currentUser.id) && 
            currentUser.role_num === 3;
    },

    async loadTransferEligibleUsers() {
      try {
        const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
        const currentUserRole = currentUser.role_num;
        
        console.log('Current user:', currentUser);
        console.log('Task collaborators:', this.taskCollaborators);
        console.log('All users:', this.users);
        
        // First, convert collaborator IDs to full user objects from the users array
        let eligibleUsers = [];
        
        if (this.taskCollaborators && this.taskCollaborators.length > 0) {
          // Map collaborators to full user objects
          eligibleUsers = this.taskCollaborators.map(collaborator => {
            // Handle both object format {id, name} and simple ID format
            const collaboratorId = typeof collaborator === 'object' ? collaborator.id : collaborator;
            
            // Find the full user object from the users array (this has the role_num)
            const fullUser = this.users.find(user => 
              String(user.id) === String(collaboratorId)
            );
            
            return fullUser;
          }).filter(user => user !== undefined); // Remove any undefined matches
        }
        
        console.log('Eligible users before filtering:', eligibleUsers);
        
        // Managers (role_num = 3) can only transfer to staff (role_num = 4)
        if (currentUserRole === 3) {
          this.transferEligibleUsers = eligibleUsers
            .filter(user => {
              const userRole = user.role_num || user.rank || 4;
              const isStaff = userRole === 4;
              const isNotCurrentUser = String(user.id) !== String(currentUser.id);
              
              console.log(`User ${user.name}: role=${userRole}, isStaff=${isStaff}, isNotCurrentUser=${isNotCurrentUser}`);
              
              return isStaff && isNotCurrentUser;
            })
            .sort((a, b) => {
              const roleA = a.role_num || a.rank || 4;
              const roleB = b.role_num || b.rank || 4;
              if (roleA !== roleB) return roleA - roleB;
              return a.name.localeCompare(b.name);
            });
        } else {
          this.transferEligibleUsers = [];
        }
        
        console.log('Final eligible users:', this.transferEligibleUsers);
        
      } catch (error) {
        console.error('Error loading transfer eligible users:', error);
        this.transferEligibleUsers = [];
      }
    },

    // Get explanation for transfer restrictions
    getTransferRestrictionExplanation() {
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
      
      if (currentUser.role_num === 3) {
        return `As a manager, you can only transfer ownership to staff members who are assigned to this ${this.isSubtask ? 'subtask' : 'task'}.`;
      } else {
        return `Only managers can transfer ${this.isSubtask ? 'subtask' : 'task'} ownership.`;
      }
    },

    // Transfer ownership
    async transferOwnership() {
      if (!this.selectedNewOwner || this.transferring) return;
      
      try {
        this.transferring = true;
        
        // Update the task's owner field using the imported service
        const updateData = {
          owner: this.selectedNewOwner
        };

        // Check if it's a subtask or task
        if (this.isSubtask) {
          // Use updateSubtask for subtasks
          await taskService.updateSubtask(this.task.id, updateData);
        } else {
          // Use updateTask for tasks
          await taskService.updateTask(this.task.id, updateData);
        }
        
        // Emit success event to parent
        this.$emit('transfer-success', {
          newOwnerId: this.selectedNewOwner,
          message: `${this.isSubtask ? 'Subtask' : 'Task'} ownership transferred successfully!`
        });
        
        // ❌ REMOVE THIS LINE - Don't close the modal automatically
        // this.closeModal();
        
      } catch (error) {
        console.error('Error transferring ownership:', error);
        this.$emit('transfer-error', `Failed to transfer ownership: ${error.message}`);
      } finally {
        this.transferring = false;
      }
    },

    // Cancel confirmation
    cancelConfirmation() {
      this.showConfirmationModal = false;
    },

    // Add this method if it doesn't exist
    selectUser(userId) {
      console.log('🔍 User clicked:', userId);
      this.selectedNewOwner = userId;
      console.log('✅ selectedNewOwner set to:', this.selectedNewOwner);
      console.log('❌ Should NOT transfer automatically yet');
    },

    showTransferConfirmation() {
      console.log('🎯 showTransferConfirmation called');
      if (!this.selectedNewOwner || this.transferring) {
        console.log('❌ Cannot show confirmation');
        return;
      }
      console.log('✅ Showing confirmation modal');
      this.showConfirmationModal = true;
    },

    async confirmTransferOwnership() {
      console.log('🚀 confirmTransferOwnership called - USER CLICKED CONFIRM');
      this.showConfirmationModal = false;
      await this.transferOwnership();
    },
  }
}
</script>

<style scoped>
/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 24px;
}

.transfer-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.current-owner-info h4,
.new-owner-selection h4 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 12px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.user-avatar.creator {
  background: #e0e7ff;
  color: #3730a3;
}

.user-avatar.assignee {
  background: #fef3c7;
  color: #92400e;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 2px 0;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.no-eligible-users {
  padding: 20px;
  background: #fef3c7;
  border-radius: 8px;
  text-align: center;
}

.no-eligible-users p {
  margin: 0 0 8px 0;
  color: #92400e;
}

.explanation {
  font-size: 14px;
  font-style: italic;
}

.user-selection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.user-selection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-selection-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.user-selection-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.selection-indicator {
  margin-left: auto;
  font-size: 18px;
  color: #10b981;
  font-weight: bold;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.transfer-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.transfer-btn:hover:not(:disabled) {
  background: #2563eb;
}

.transfer-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.confirm-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.confirm-btn:hover {
  background: #059669;
}

.confirm-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.3);
}

.confirmation-text {
  margin-bottom: 16px;
  color: #374151;
}

.warning-text {
  margin-bottom: 24px;
  color: #dc2626;
  font-style: italic;
}
</style>
