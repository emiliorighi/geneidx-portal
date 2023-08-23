import http from '../../http-axios'

const base = http.base

class GeneidService {

  sendForm(formData) {
    return base.post('/geneid', formData)
  }
}

export default new GeneidService()
