<template>
  <el-container>
    <el-header>
        <top-navbar />
    </el-header>
    <el-main>
      <p>The user is only used to filter the texts.</p>
      <div style="margin: 20px;"></div>
      <el-form ref="loginForm" :model="loginForm" :rules="rules" label-width="120px" size="medium">
      <el-form-item label="Username" prop="username">
        <el-input v-model="loginForm.username"></el-input>
      </el-form-item>
      <el-form-item label="Password" prop="password">
        <el-input v-model="loginForm.password"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="login()">Login</el-button>
        <el-button type="primary" @click="register()">Register</el-button>
      </el-form-item>
      </el-form>
    </el-main>
  </el-container>
</template>
  
<script>
import TopNavbar from './TopNav/TopNavbar.vue';
export default {
  components: {
    TopNavbar,
  },
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
      },
      rules: {
        username: [
          { required: true, message: 'Please input your username', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please input your password', trigger: 'blur' }
        ],
      }
    };
  },
  methods: {
    async register() {
      console.log(this.data);
      console.log('submit');
      const response = await fetch("http://localhost:8000/user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: this.loginForm.username,
          password: this.loginForm.password,
        })
      });
      console.log(response);
    },
    async login() {
      const response = await fetch("http://localhost:8000/user", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: this.loginForm.username,
          password: this.loginForm.password,
        })
      });
      console.log(response);
    },
  }
};
  </script>
  