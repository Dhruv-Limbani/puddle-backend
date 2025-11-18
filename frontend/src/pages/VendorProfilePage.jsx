import React from 'react'
import { useParams } from 'react-router-dom'
import PublicVendorProfile from '../components/PublicVendorProfile'

export default function VendorProfilePage() {
  const { vendorId } = useParams()
  return <PublicVendorProfile vendorId={vendorId} />
}
