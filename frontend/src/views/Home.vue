<template>
  <div>
    <h1>Dashboard</h1>
    
    <hr>
    <TotalTaskCount />
    
    <hr>
    <TasksByStatus />
    
    <hr>
    <TasksByStaff />
    
    <hr>
    <PendingTasksByAge />
  </div>
</template>

<script>
import TotalTaskCount from '@/components/Dashboard/TotalTaskCount.vue';
import TasksByStatus from '@/components/Dashboard/TasksByStatus.vue';
import TasksByStaff from '@/components/Dashboard/TasksByStaff.vue';
import PendingTasksByAge from '@/components/Dashboard/PendingTasksByAge.vue';

export default {
  name: 'Home',
  components: {
    TotalTaskCount,
    TasksByStatus,
    TasksByStaff,
    PendingTasksByAge,
  },
  mounted() {
    console.log('Home.vue mounted - All components should load');
  }
}
</script>