# Speed Reader

A customizable speed reading application built with Python and Tkinter that helps users improve their reading speed while maintaining comprehension.

## Features

### Core Functionality
- Adjustable reading speed (100-1000 WPM)
- Variable word grouping (1-5 words at a time)
- Text file loading support
- Pause/Resume/Stop controls
- Progress tracking with time remaining

### Advanced Reading Features
- Dynamic font sizing based on window dimensions
- Focus point indicator for optimal word recognition
- Intelligent timing adjustments:
  - Variable delays based on word length
  - Automatic pauses at punctuation marks
  - Special handling for longer words and complex punctuation
- Text preprocessing for better readability

### User Interface
- Minimalist reading mode
- Full control panel for settings
- Progress bar
- Responsive design that adapts to window size
- Dark theme for reduced eye strain

## Installation

1. Ensure you have Python 3.6 or later installed on your system.
2. Install the required dependencies:
```bash
pip install tkinter
```
Note: Tkinter usually comes with Python installations by default.

## Usage

### Running the Program
1. Navigate to the program directory
2. Run the program:
```bash
python speed_reader.py
```

### Basic Controls
- **Start**: Begin reading the loaded text
- **Pause/Continue**: Temporarily stop reading and show control panel
- **Stop**: End the reading session
- **Load Text**: Open a text file for reading

### Reading Settings
- **WPM Slider**: Adjust reading speed from 100 to 1000 words per minute
- **Words per Display**: Choose how many words to show at once (1-5)

### Advanced Features
- The focus point indicator (▼) helps guide your eyes to the optimal reading position
- Longer words and punctuation marks automatically adjust the reading speed
- Window can be resized to adjust text display size

## Tips for Effective Use

1. **Start Slow**: Begin with lower WPM settings (200-300) and gradually increase speed
2. **Use the Focus Point**: Keep your eyes on the focus indicator for better comprehension
3. **Word Grouping**: Start with single words and increase grouping as you improve
4. **Take Breaks**: Speed reading can be mentally intensive; take regular breaks
5. **Practice Regularly**: Consistent practice will help improve reading speed and comprehension

## Customization

The program includes several customizable features:

- Punctuation delays can be adjusted in the code
- Word length thresholds for timing adjustments
- Focus point positioning
- Color scheme and fonts
- Window size and text scaling

## Technical Details

Built using:
- Python 3.x
- Tkinter for GUI
- Threading for smooth performance
- Regular expressions for text processing

## Known Limitations

- Currently only supports plain text (.txt) files
- Number-to-word conversion is limited
- Maximum window size depends on screen resolution

## Contributing

Feel free to fork this project and submit pull requests for any improvements:
- Additional file format support
- Enhanced text processing features
- UI/UX improvements
- Performance optimizations

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with accessibility and user experience in mind
- Inspired by various speed reading techniques and research
- Thanks to the Python and Tkinter communities