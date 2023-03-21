CREATE TABLE Caregivers (
    Username varchar(255) PRIMARY KEY,
    Salt BINARY(16),
    Hash BINARY(16),
);

CREATE TABLE Availabilities (
    Time date,
    caregiver_id varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, caregiver_id)
);

CREATE TABLE Patients (
    Username varchar(255) PRIMARY KEY,
    Salt BINARY(16),
    Hash BINARY(16)
);


CREATE TABLE Vaccines (
    Name varchar(255) PRIMARY KEY,
    Doses int
);

CREATE TABLE Appointments (
    appointment_id varchar(255) PRIMARY KEY,
    patient_id varchar(255) REFERENCES Patients,
    vaccine_used varchar(255) REFERENCES Vaccines,
    caregiver_id varchar(255),
    Time date
);
