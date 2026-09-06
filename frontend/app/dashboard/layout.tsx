export const metadata = {
  title: 'Tử Vi GraphRAG',
  description: 'Lập lá số Tử Vi và luận giải với GraphRAG.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
