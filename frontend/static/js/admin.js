function adminData() {
  return {
    adminTab: "overview",

    stats: { doctorCount: 0, patientCount: 0, appointmentCount: 0 },


    doctorList:  [],
    docSearch:   "",
    docFlash:    "",
    docError:    "",
    doctorModal: { show: false, mode: "add", id: null },
    doctorForm:  { name: "", email: "", password: "", specialization: "", experience: 0 },


    patientList: [],
    patSearch:   "",
    patFlash:    "",


    appointmentList: [],
    apptFilter:      "",

    departments: [],
    deptModal:   false,
    deptForm:    { name: "", description: "" },
    deptFlash:   "",
    deptError:   "",


    globalQ:       "",
    searchResults: null,
    searchTab:     "doctors",


    formLoading: false,
  };
}


const adminComputed = {

  filteredDoctors() {
    const q = this.docSearch.toLowerCase();
    return this.doctorList.filter(
      (d) =>
        d.name.toLowerCase().includes(q) ||
        d.specialization.toLowerCase().includes(q)
    );
  },

  filteredPatients() {
    const q = this.patSearch.toLowerCase();
    return this.patientList.filter(
      (p) =>
        p.name.toLowerCase().includes(q) || p.contact.includes(q)
    );
  },


  filteredAppts() {
    if (!this.apptFilter) return this.appointmentList;
    return this.appointmentList.filter((a) => a.status === this.apptFilter);
  },
};

const adminMethods = {


  fetchStats() {
    axios
      .get("/api/admin/dashboard")
      .then((res) => { this.stats = res.data; })
      .catch(() => {});
  },


  fetchDoctors() {
    axios
      .get("/api/admin/doctors")
      .then((res) => { this.doctorList = res.data; })
      .catch(() => {});
  },

  openAddDoctor() {
    this.docError   = "";
    this.doctorForm = { name: "", email: "", password: "", specialization: "", experience: 0 };
    this.doctorModal = { show: true, mode: "add", id: null };
  },


  openEditDoctor(doc) {
    this.docError   = "";
    this.doctorForm = {
      name: doc.name,
      email: doc.email,
      password: "",
      specialization: doc.specialization,
      experience: doc.experience,
    };
    this.doctorModal = { show: true, mode: "edit", id: doc.id };
  },

  submitDoctorForm() {
    this.docError = "";
    const { mode, id } = this.doctorModal;
    const form = this.doctorForm;

    if (!form.name || !form.specialization) {
      this.docError = "Name and specialization are required.";
      return;
    }
    if (mode === "add" && (!form.email || !form.password)) {
      this.docError = "Email and password are required.";
      return;
    }

    this.formLoading = true;
    const req =
      mode === "add"
        ? axios.post("/api/admin/doctors", form)
        : axios.put(`/api/admin/doctors/${id}`, form);

    req
      .then(() => {
        const msg = mode === "add" ? "Doctor added successfully." : "Doctor updated.";
        this.docFlash         = msg;
        this.doctorModal.show = false;
        this.formLoading      = false;
        this.fetchDoctors();
        this.fetchStats();
        this.showToast(msg, "success");
        setTimeout(() => { this.docFlash = ""; }, 3000);
      })
      .catch((err) => {
        this.docError    = err.response?.data?.error || "Something went wrong.";
        this.formLoading = false;
      });
  },

  toggleDoctor(doc) {
    const action = doc.isActive ? "blacklist" : "activate";
    if (!confirm(`Are you sure you want to ${action} Dr. ${doc.name}?`)) return;
    axios
      .post(`/api/admin/doctors/${doc.id}/toggle`)
      .then((res) => {
        doc.isActive  = res.data.isActive;
        this.docFlash = res.data.message;
        this.showToast(res.data.message, "success");
        setTimeout(() => { this.docFlash = ""; }, 3000);
      })
      .catch(() => {});
  },


  fetchPatients() {
    axios
      .get("/api/admin/patients")
      .then((res) => { this.patientList = res.data; })
      .catch(() => {});
  },


  togglePatient(pat) {
    const action = pat.isActive ? "block" : "unblock";
    if (!confirm(`${action} patient ${pat.name}?`)) return;
    axios
      .post(`/api/admin/patients/${pat.id}/toggle`)
      .then((res) => {
        pat.isActive  = res.data.isActive;
        this.patFlash = `Patient ${action}ed.`;
        this.showToast(`Patient ${action}ed.`, "success");
        setTimeout(() => { this.patFlash = ""; }, 3000);
      })
      .catch(() => {});
  },

  fetchAdminAppointments() {
    axios
      .get("/api/admin/appointments")
      .then((res) => { this.appointmentList = res.data; })
      .catch(() => {});
  },

  fetchDepartments() {
    axios
      .get("/api/departments")
      .then((res) => { this.departments = res.data; })
      .catch(() => {});
  },


  doctorsByDept(deptName) {
    return (
      this.doctorList.filter((d) => d.specialization === deptName).length +
      " doctor(s)"
    );
  },


  submitDept() {
    this.deptError = "";
    if (!this.deptForm.name.trim()) {
      this.deptError = "Department name is required.";
      return;
    }
    this.formLoading = true;
    axios
      .post("/api/departments", this.deptForm)
      .then(() => {
        this.deptFlash   = "Department added.";
        this.deptModal   = false;
        this.deptForm    = { name: "", description: "" };
        this.formLoading = false;
        this.fetchDepartments();
        this.showToast("Department added.", "success");
        setTimeout(() => { this.deptFlash = ""; }, 3000);
      })
      .catch((err) => {
        this.deptError   = err.response?.data?.error || "Could not add department.";
        this.formLoading = false;
      });
  },

  runSearch() {
    if (!this.globalQ.trim()) return;
    axios
      .get("/api/admin/search", { params: { q: this.globalQ } })
      .then((res) => { this.searchResults = res.data; })
      .catch(() => {});
  },
};
