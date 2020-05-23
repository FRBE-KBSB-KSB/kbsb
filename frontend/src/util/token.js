export function oAuth2token(token) {
  return  { 
    authorized: { 
      OAuth2PasswordBearer: {
        token: {
          access_token: token 
        }
      }
    }
  }
} 