from PIL import Image
from pathlib import Path
import shutil
from typing import Tuple, Generator
import pandas as pd


class EmzConverter:

    def __init__(self, folder_input_path: str, folder_output_path: str = None, output_type: str = "png"):
        """
        A process that converts the emz files within a folder to an output type.
        Args:
            folder_input_path: The path in which the emz files are located.
            folder_output_path: The path you want to store the output files, defaults to None.
             If nothing is provided, then the process will store the outputs in a new sub-folder under the input path
             named output_png_images.
            output_type: The type with which you want to store the images. Defaults to png.
        """

        self.folder_input_path, self.folder_output_path = self.check_paths(folder_input_path=folder_input_path,
                                                                           folder_output_path=folder_output_path)

        self.wmf_folder = self.folder_input_path / "wmf_files"

        self.wmf_folder.mkdir(parents=True, exist_ok=True)

        self.output_type = output_type
        
    @staticmethod
    def check_paths(folder_input_path: str, folder_output_path: str) -> Tuple[Path, Path]:
        """
        Checks the provided paths and generates the folder output path if None is provided as the the output path.
        Args:
            folder_input_path: The folder where the emz files live.
            folder_output_path: The folder in which the results will be stored.

        Returns:
            The two paths as Path types.

        Raises:
            IOError: If the input path does not exist.
        """
        if not Path(folder_input_path).exists():
            raise IOError(f"The path {folder_input_path} does not exist")

        if folder_output_path is None:
            folder_output_path = folder_input_path + "\\output_png_images"

        if not Path(folder_output_path).exists():
            Path(folder_output_path).mkdir(parents=True)
        return Path(folder_input_path), Path(folder_output_path)

    @staticmethod
    def find_files(path: Path, suffix: str):
        """
        Lists all the files with a given suffix under a folder.

        Args:
            path: The path you are interested in.
            suffix: The suffix you are interested in.

        Returns:
            A generator with the files having the given suffix in the given path.
        """
        if not path.exists():
            raise IOError("Provided path does not exist.")
        return path.glob(f"*.{suffix}")

    def convert_emz_files_to_wmf(self) -> None:
        """Converts the emz files within the input path to wmf in order to read them with Pil Image."""
        emz_files = list(self.find_files(path=self.folder_input_path, suffix="emz"))
        print(f"Found {len(emz_files)} emz files in folder {self.folder_input_path}."
              f"Renaming files to .wmf and copying to the folder {self.wmf_folder}")
        for file_ in emz_files:
            file_wmf = self.wmf_folder / file_.with_suffix(".wmf").name
            shutil.copyfile(str(file_), str(file_wmf))

    def convert_wmf_to_specified_output_type(self) -> None:
        """Converts wmf files to specified ouptup_type."""
        errors_ = []
        for file_ in self.find_files(self.wmf_folder, suffix="wmf"):
            try:
                image_ = Image.open(file_)
                file_output_type = self.folder_output_path / file_.with_suffix(f".{self.output_type}").name
                image_.save(file_output_type)
            except Exception as e:
                print(f"Creating png out of emz was unsuccessful for the file: {file_}. The error was {e}")
                errors_.append(file_)
                continue
        shutil.rmtree(self.wmf_folder)
        if len(errors_) > 0:
            csv_file = str(Path(".") / "unsuccessful_conversions.csv")
            pd.DataFrame(errors_, columns=["file_names"]).to_csv(csv_file)
            raise Exception(f"Some files were not updated. \n"
                            f"Check this csv [{csv_file}] for a detailed list of files that did not update")
        else:
            print("Process completed. Deleting wmf files.")

    def convert(self):
        print(f"Converting EMZ files from {self.folder_input_path} to {self.folder_output_path}")
        self.convert_emz_files_to_wmf()
        self.convert_wmf_to_specified_output_type()


if __name__ == '__main__':
    EmzConverter(folder_input_path=r"C:\Users\c.spanachis\PycharmProjects\emz_convertor").convert()
