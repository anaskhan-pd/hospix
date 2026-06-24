function doctorData() {
  return {

    docTab: "appointments",

    docAppointments: [],
    docApptFilter:   "",
    docApptFlash:    "",
    docApptError:    "",

    docPatients:        [],
    docPatSearch:       "",
    selectedDocPatient: null,

    availFlash:    "",
    selectedDates: [],
    next7Days:     [],

    treatmentModal: {
      show: false,
      apptId: null,
      patientName: "",
      date: "",
      timeSlot: "",
    },
    treatmentForm: { diagnosis: "", prescription: "", notes: "" },
  };
}

const doctorComputed = {

  filteredDocAppts() {
    if (!this.docApptFilter) return this.docAppointments;
    return this.docAppointments.filter(
      (a) => a.status === this.docApptFilter
    );
  },

  filteredDocPatients() {
    const q = this.docPatSearch.toLowerCase();
    return this.docPatients.filter((p) =>
      p.name.toLowerCase().includes(q)
    );
  },
};

const doctorMethods = {

  fetchDocAppointments() {
    axios
      .get("/api/doctor/appointments")
      .then((res) => { this.docAppointments = res.data; })
      .catch(() => {});
  },

  openTreatmentModal(appt) {
    this.docApptError  = "";
    this.treatmentForm = { diagnosis: "", prescription: "", notes: "" };
    this.treatmentModal = {
      show:        true,
      apptId:      appt.id,
      patientName: appt.patient_name,
      date:        appt.date,
      timeSlot:    appt.time_slot,
    };
  },

  submitTreatment() {
    if (!this.treatmentForm.diagnosis.trim()) {
      this.docApptError = "Diagnosis is required.";
      return;
    }
    this.formLoading = true;
    axios
      .post(
        `/api/doctor/appointments/${this.treatmentModal.apptId}/complete`,
        this.treatmentForm
      )
      .then(() => {
        this.treatmentModal.show = false;
        this.formLoading         = false;
        this.docApptFlash        = "Appointment marked as completed.";
        this.fetchDocAppointments();
        this.showToast("Appointment marked as completed.", "success");
        setTimeout(() => { this.docApptFlash = ""; }, 3000);
      })
      .catch((err) => {
        this.docApptError = err.response?.data?.error || "Something went wrong.";
        this.formLoading  = false;
      });
  },

  docCancelAppt(appt) {
    if (!confirm(`Cancel appointment for ${appt.patient_name} on ${appt.date}?`))
      return;
    axios
      .post(`/api/doctor/appointments/${appt.id}/cancel`)
      .then(() => {
        this.docApptFlash = "Appointment cancelled.";
        this.fetchDocAppointments();
        this.showToast("Appointment cancelled.", "info");
        setTimeout(() => { this.docApptFlash = ""; }, 3000);
      })
      .catch(() => {});
  },

  fetchDocPatients() {
    axios
      .get("/api/doctor/patients")
      .then((res) => { this.docPatients = res.data; })
      .catch(() => {});
  },

  initAvailability() {
    const dayNames = [
      "Sunday","Monday","Tuesday",
      "Wednesday","Thursday","Friday","Saturday",
    ];
    this.next7Days = [];
    for (let i = 0; i < 7; i++) {
      const d     = new Date();
      d.setDate(d.getDate() + i);
      const value = d.toISOString().split("T")[0];
      const label = dayNames[d.getDay()];
      this.next7Days.push({ value, label });
    }
  },

  saveAvailability() {
    axios
      .post("/api/doctor/availability", { dates: this.selectedDates })
      .then(() => {
        this.availFlash = "Availability saved successfully.";
        this.showToast("Availability saved successfully.", "success");
        setTimeout(() => { this.availFlash = ""; }, 3000);
      })
      .catch(() => {});
  },
};
