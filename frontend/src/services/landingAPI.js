import { APP_CONFIG } from '../utils/constants'

class LandingAPI {
  constructor() {
    this.baseURL = `${APP_CONFIG.apiBaseUrl}/api/landing`
  }

  async getLandingInfo() {
    try {
      const response = await fetch(`${this.baseURL}/info`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching landing info:', error)
      throw error
    }
  }

  async getFeatures() {
    try {
      const response = await fetch(`${this.baseURL}/features`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching features:', error)
      throw error
    }
  }

  async getPricing() {
    try {
      const response = await fetch(`${this.baseURL}/pricing`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching pricing:', error)
      throw error
    }
  }

  async getCompanyInfo() {
    try {
      const response = await fetch(`${this.baseURL}/company`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching company info:', error)
      throw error
    }
  }

  async getPublicStats() {
    try {
      const response = await fetch(`${this.baseURL}/stats`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching public stats:', error)
      throw error
    }
  }
}

export const landingAPI = new LandingAPI()
export default landingAPI