from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from server.database.handler import TaskDatabaseHandler
from server.models.job import Job
from server.schemas.job_schema import JobCreate, JobUpdate, JobResponse


router = APIRouter()


@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(TaskDatabaseHandler().get_db)):
    db_job = Job(language=job.language, filename=job.filename, state=job.state, verdict=job.verdict)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(TaskDatabaseHandler().get_db)):
    # breakpoint()
    return db.query(Job).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(TaskDatabaseHandler().get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(TaskDatabaseHandler().get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.state is not None:
        db_job.state = job.state
    if job.verdict is not None:
        db_job.verdict = job.verdict
    db.commit()
    db.refresh(db_job)
    return db_job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(TaskDatabaseHandler().get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"message": "Job deleted successfully"}
