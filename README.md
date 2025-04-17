# Profileinator

Profileinator is a web application that generates AI profile pictures from user-uploaded photos.
It uses OpenAI's GPT-4o and DALL-E 3 models to create stylish, professional variants of your photos suitable for various platforms.

Right now it's sorta like a game of telephone.
GPT-4o describes the picture in text and sends the text to DALL-E, which creates the image.
Hilarity ensues.

## Features

- Upload any image to use as a base for your profile pictures
- Generate multiple AI-enhanced profile picture variants
- Preview and download the generated images
- Simple, responsive user interface
- No user data stored on the server

## Technical Stack

- **Backend**: FastAPI (Python 3.13+)
- **Frontend**: HTML, CSS, JavaScript (no framework)
- **AI**: OpenAI GPT-4o, DALL-E 3
- **Development Tools**: pyright, ruff, pytest
- **Package Management**: uv

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv package manager
- OpenAI API key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/austin3dickey/profileinator.git
   cd profileinator
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```

### Running the Application

```bash
uv run profileinator
```

The application will be available at [http://localhost:8000](http://localhost:8000)

## Development

### Linting

```bash
uv run ruff check .
```

### Formatting

```bash
uv run ruff format .
```

### Type Checking

```bash
uv run pyright
```

### Running Tests

```bash
uv run pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT-4o model
- FastAPI for the web framework
