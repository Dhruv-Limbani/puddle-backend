import React from 'react'
import { useParams } from 'react-router-dom'
import DatasetProfile from '../components/DatasetProfile'

export default function DatasetProfilePage() {
  const { datasetId } = useParams()
  return <DatasetProfile datasetId={datasetId} />
}
