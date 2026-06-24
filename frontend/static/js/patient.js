function patientData() {
  return {
    patTab: "doctors",

    doctorSearchList:  [],
    docSpecFilter:     "",
    allDepartments:    [],

    bookingDoctor:     null,
    bookingModal:      false,
    bookingForm:       { date: "", time_slot: "", reason: "" },
    bookingFlash:      "",
    bookingError:      "",

    myAppointments:    [],
    myApptFilter:      "",

    myProfile:         {},
    profileForm:       { name: "", contact: "", address: "", age: "" },
    profileFlash:      "",
    profileError:      "",
    editingProfile:    false,

    exportMsg:         "",
  };
}

const patientComputed = {

  filteredMyAppts() {
    if (!this.myApptFilter) return this.myAppointments;
    return this.myAppointments.filter(
      (a) => a.status === this.myApptFilter
    );
  },

  upcomingAppts() {
    const today = new Date().toISOString().split("T")[0];
    return this.myAppointments.filter(
      (a) => a.status === "booked" && a.date >= today
    );
  },

  pastAppts() {
    return this.myAppointments.filter(
      (a) => a.status === "completed" || a.status === "cancelled"
    );
  },
};

const patientMethods = {

  fetchAllDepartments() {
    axios
      .get("/api/departments")
      .then((res) => { this.allDepartments = res.data; })
      .catch(() => {});
  },

  searchDoctors() {
    axios
      .get("/api/doctors/search", {
        params: { specialization: this.docSpecFilter },
      })
      .then((res) => { this.doctorSearchList = res.data; })
      .catch(() => {});
  },


  openBooking(doctor) {
    this.bookingError  = "";
    this.bookingForm   = { date: "", time_slot: "", reason: "" };
    this.bookingDoctor = doctor;
    this.bookingModal  = true;
  },

  submitBooking() {
    this.bookingError = "";
    const f = this.bookingForm;

    if (!f.date || !f.time_slot) {
      this.bookingError = "Please select a date and time slot.";
      return;
    }

    this.formLoading = true;
    axios
      .post("/api/patient/appointments", {
        doctor_id: this.bookingDoctor.id,
        date:      f.date,
        time_slot: f.time_slot,
        reason:    f.reason,
      })
      .then(() => {
        this.bookingModal = false;
        this.formLoading  = false;
        this.bookingFlash = "Appointment booked successfully!";
        this.fetchMyAppointments();
        this.showToast("Appointment booked successfully!", "success");
        setTimeout(() => { this.bookingFlash = ""; }, 3000);
      })
      .catch((err) => {
        this.bookingError = err.response?.data?.error || "Booking failed.";
        this.formLoading  = false;
      });
  },

  fetchMyAppointments() {
    axios
      .get("/api/patient/appointments")
      .then((res) => { this.myAppointments = res.data; })
      .catch(() => {});
  },

  cancelMyAppt(appt) {
    if (!confirm(`Cancel your appointment with Dr. ${appt.doctor_name} on ${appt.date}?`))
      return;
    axios
      .post(`/api/patient/appointments/${appt.id}/cancel`)
      .then(() => {
        this.fetchMyAppointments();
        this.showToast("Appointment cancelled.", "info");
      })
      .catch(() => {});
  },

  fetchMyProfile() {
    axios
      .get("/api/patient/profile")
      .then((res) => {
        this.myProfile  = res.data;
        this.profileForm = {
          name:    res.data.name,
          contact: res.data.contact,
          address: res.data.address,
          age:     res.data.age,
        };
      })
      .catch(() => {});
  },


  saveProfile() {
    this.profileError = "";
    axios
      .put("/api/patient/profile", this.profileForm)
      .then(() => {
        this.profileFlash  = "Profile updated successfully.";
        this.editingProfile = false;
        this.fetchMyProfile();
        this.showToast("Profile updated successfully.", "success");
        setTimeout(() => { this.profileFlash = ""; }, 3000);
      })
      .catch((err) => {
        this.profileError = err.response?.data?.error || "Update failed.";
      });
  },


  triggerExport() {
        window.location.href = "/api/patient/export-csv";
    },
};