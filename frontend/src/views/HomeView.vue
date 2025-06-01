<script setup lang="ts">
// No script needed for now as per the new requirements
// import { useRouter } from 'vue-router'
// const router = useRouter()
</script>

<template>
  <div class="home-view">
    <section class="project-introduction">
      <h1>项目介绍</h1>
      <p>欢迎来到 AI 小说创作助手！</p>
    </section>

    <nav class="main-menu">
      <ul>
        <li><router-link to="/my-novels">我的小说</router-link></li>
        <li><router-link to="/create-novel">创建小说</router-link></li>
        <li><router-link to="/brain-generator">脑洞生成器</router-link></li>
        <li><router-link to="/character-templates">角色模板</router-link></li>
      </ul>
    </nav>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.project-introduction {
  margin-bottom: 40px;
  text-align: center;
}

.project-introduction h1 {
  font-size: 2.5em;
  color: #333;
  margin-bottom: 10px;
}

.project-introduction p {
  font-size: 1.2em;
  color: #666;
}

.main-menu ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap; /* Allows items to wrap on smaller screens */
  justify-content: center;
  gap: 20px; /* Spacing between menu items */
}

.main-menu li {
  margin: 0; /* Removed individual margins as gap is used */
}

.main-menu a {
  display: block;
  padding: 15px 25px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
}

.main-menu a:hover,
.main-menu a:focus {
  background-color: #0056b3;
  outline: none; /* Improves accessibility */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .main-menu ul {
    flex-direction: column; /* Stack items vertically on smaller screens */
    align-items: center;
  }

  .main-menu li {
    width: 100%; /* Make menu items take full width */
    max-width: 300px; /* Optional: constrain max width */
    margin-bottom: 10px; /* Add some space between stacked items */
  }

  .main-menu a {
    text-align: center; /* Center text for stacked items */
  }

  .project-introduction h1 {
    font-size: 2em;
  }

  .project-introduction p {
    font-size: 1em;
  }
}
</style>
