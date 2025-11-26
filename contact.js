export default async function handler(req, res) {
  if(req.method === 'POST'){
    const { name, email, message } = req.body;
    console.log({ name, email, message });
    return res.status(200).json({ message: 'Thank you! Your message was sent.' });
  }
  return res.status(405).json({ error: 'Method Not Allowed' });
}
