from abc import ABC, abstractmethod

# Base class for GNSS data sources
class GNSSDataSource(ABC):
    @abstractmethod
    def read_data(self):
        pass

# Derived class for GNSS data from UART
class UARTDataSource(GNSSDataSource):
    def read_data(self):
        # Reading data from UART
        data = []
        return data

# Derived class for GNSS data from USB
class USBDataSource(GNSSDataSource):
    def read_data(self):
        # Reading data from USB
        data = []
        return data

# Derived class for GNSS data from a File
class FileDataSource(GNSSDataSource):
    def __init__(self, filename):
        self.filename = filename

    def read_data(self):
        try:
            with open(self.filename, 'r') as file:
                data = []
                for line in file:
                    # Parse and add data from the file
                    values = line.strip().split(',')
                    if len(values) == 5:
                        data.append([float(value) for value in values])
                return data
        except FileNotFoundError:
            print("File not found.")
            return []

# Factory class for creating GNSS data sources
class GNSSDataSourceFactory:
    @staticmethod
    def create_data_source(source_type, source_parameter=None):
        if source_type == "UART":
            return UARTDataSource()
        elif source_type == "USB":
            return USBDataSource()
        elif source_type == "File" and source_parameter is not None:
            return FileDataSource(source_parameter)
        else:
            raise ValueError("Invalid data source type")


# Example usage:
if __name__ == "__main__":
    data_source_type = "File"  # Change this to "UART" or "USB" for other source types
    file_path = "gnss_data.txt"  # Specify the file path if using "File" source

    try:
        data_source = GNSSDataSourceFactory.create_data_source(data_source_type, file_path)
        gnss_data = data_source.read_data()
        if not gnss_data:
            print("No GNSS data available.")
        else:
            print("GNSS data:", gnss_data)
    except ValueError as e:
        print(e)
