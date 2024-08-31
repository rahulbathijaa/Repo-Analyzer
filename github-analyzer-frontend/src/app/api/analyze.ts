import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { username } = req.query;
  const response = await fetch(`YOUR_PYTHON_BACKEND_URL/analyze_repos?username=${username}`);
  const data = await response.json();
  res.status(200).json(data);
}
