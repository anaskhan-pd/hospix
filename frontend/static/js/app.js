const { createApp } = Vue;

createApp({

  data() {
    return {
      loggedIn: false,
      authTab: "login",
      loginEmail: "",
      loginPassword: "",
      authError: "",
      authSuccess: "",
      authLoading: false,

      reg: {
        name: "", email: "", password: "",
        age: "", gender: "", contact: "", address: "",
      },

      role: "",
      userName: "",

      // UI state
      sidebarOpen: false,
      toasts: [],
      toastCounter: 0,

      ...adminData(),
      ...doctorData(),
      ...patientData(),
    };
  },


  computed: {
    ...adminComputed,
    ...doctorComputed,
    ...patientComputed,
  },


  mounted() {
    axios
      .get("/api/check-session")
      .then((res) => {
        if (res.data.loggedIn) {
          this.loggedIn = true;
          this.role = res.data.role;
          this.userName = res.data.name;
          this.onLoginSuccess();
        }
      })
      .catch(() => { });
  },

  methods: {
    // ── Toast system ──
    showToast(msg, type = "success") {
      const id = ++this.toastCounter;
      this.toasts.push({ id, msg, type, removing: false });
      setTimeout(() => { this.removeToast(id); }, 3200);
    },

    removeToast(id) {
      const t = this.toasts.find(t => t.id === id);
      if (t && !t.removing) {
        t.removing = true;
        setTimeout(() => {
          this.toasts = this.toasts.filter(t => t.id !== id);
        }, 250);
      }
    },

    // ── Auth ──
    handleLogin() {
      this.authError = "";
      this.authLoading = true;
      axios
        .post("/api/login", {
          email: this.loginEmail,
          password: this.loginPassword,
        })
        .then((res) => {
          this.loggedIn = true;
          this.role = res.data.role;
          this.userName = res.data.name;
          this.authLoading = false;
          this.onLoginSuccess();
        })
        .catch((err) => {
          this.authError = err.response?.data?.message || "Invalid credentials";
          this.authLoading = false;
        });
    },

    handleRegister() {
      this.authError = "";
      this.authSuccess = "";
      const r = this.reg;

      // frontend validation
      if (!r.name || !r.email || !r.password || !r.age || !r.gender || !r.contact || !r.address) {
        this.authError = "Please fill in all fields.";
        return;
      }

      this.authLoading = true;
      axios
        .post("/api/register", r)
        .then(() => {
          this.authSuccess = "Account created! Please log in.";
          this.authLoading = false;
          this.authTab = "login";
          this.reg = { name: "", email: "", password: "", age: "", gender: "", contact: "", address: "" };
        })
        .catch((err) => {
          this.authError = err.response?.data?.error || "Registration failed.";
          this.authLoading = false;
        });
    },

    handleLogout() {
      axios.post("/api/logout").finally(() => {
        window.location.href = "/";
      });
    },


    onLoginSuccess() {
      if (this.role === "admin") {
        this.fetchStats();
        this.fetchDoctors();
      }
      if (this.role === "doctor") {
        this.fetchDocAppointments();
      }
      if (this.role === "patient") {
        this.fetchMyAppointments();
        this.fetchMyProfile();
        this.searchDoctors();
        this.fetchAllDepartments();
      }
    },

    ...adminMethods,
    ...doctorMethods,
    ...patientMethods,
  },

}).mount("#app");
