import typing
import numpy
import numpy as npy
import math
import pya
import os

RAW_PATH_TO_KLAYOUT: str = os.getcwd()

class Touchstone(pya.QDialog):
    def __init__(self, file: typing.Union[str, typing.TextIO], from_port, to_port, plot_type, process, encoding: typing.Union[str, None] = None):
        self.snp_file = file
        self.from_port = int(from_port)
        self.to_port = int(to_port)
        self.plot_type = plot_type
        self.comments = None
        self.frequency_unit = None
        self.frequency_nb = None
        self.parameter = None
        self.format = None
        self.resistance = None
        self.reference = None
        self.sparameters = None
        self.noise = None
        self.rank = None
        self.port_names = None
        self.comment_variables = None
        self.has_hfss_port_impedances = False
        self.process = process
        
        try:
            try:
                if encoding is not None:
                    fid = self.get_fid(file, encoding=encoding)
                    self.filename = fid.name
                    self.load_file(fid)
                else:
                    fid = self.get_fid(file)
                    self.filename = fid.name
                    self.load_file(fid)
            except Exception as e:
                fid.close()
                raise e

        except UnicodeDecodeError:
            fid = self.get_fid(file, encoding='ISO-8859-1')
            self.filename = fid.name
            self.load_file(fid)

        except ValueError:
            fid = self.get_fid(file, encoding='utf-8-sig')
            self.filename = fid.name
            self.load_file(fid)

        except Exception as e:
            raise ValueError(f'Something went wrong by the file opening: {e}')

        finally:
            self.gamma = []
            self.z0 = []

            if self.has_hfss_port_impedances:
                self.get_gamma_z0_from_fid(fid)

            fid.close()
    
    def get_fid(self, file: typing.Union[str, typing.TextIO], *args, **kwargs) -> typing.TextIO:
        """Открывает файл и возвращает объект файла."""
        if isinstance(file, str):
            return open(file, *args, **kwargs)
        else:
            return file

    def load_file(self, fid: typing.TextIO) -> None:
            """Загружает файл с расширением .sNp или .ts и извлекает параметры из него.

            Аргументы:
            - fid (typing.TextIO): Открытый файловый объект
            """
            filename = self.filename
            extension = filename.split('.')[-1].lower()

            if (extension[0] == 's') and (extension[-1] == 'p'): 
                try:
                    self.rank = int(extension[1:-1])
                except (ValueError):
                    raise (ValueError("filename does not have a s-parameter extension. It has  [%s] instead. please, correct the extension to of form: 'sNp', where N is any integer." %(extension)))
            elif extension == 'ts':
                pass
            else:
                raise Exception('Filename does not have the expected Touchstone extension (.sNp or .ts)')

            values = []
            while True:
                line = fid.readline()
                if not line:
                    break
                line = line.split('!', 1)
                if len(line) == 2:
                    if not self.parameter:
                        if self.comments is None:
                            self.comments = ''
                        self.comments = self.comments + line[1]
                    elif line[1].startswith(' Port['):
                        try:
                            port_string, name = line[1].split('=', 1) 
                            name = name.strip()
                            garbage, index = port_string.strip().split('[', 1) 
                            index = int(index.rstrip(']')) 
                            if index > self.rank or index <= 0:
                                print(f"Port name {name} provided for port number {index} but that's out of range for a file with extension s{self.rank}p")
                            else:
                                if self.port_names is None: 
                                    self.port_names = [''] * self.rank
                                self.port_names[index - 1] = name
                        except ValueError as e:
                            print(f"Error extracting port names from line: {line}")
                    elif line[1].strip().lower().startswith('port impedance'):
                        self.has_hfss_port_impedances = True

                line = line[0].strip().lower()

                if len(line) == 0:
                    continue

                if line[:9] == '[version]':
                    self.version = line.split()[1]
                    continue

                if line[:11] == '[reference]':
                    self.reference = [ float(r) for r in line.split()[2:] ]
                    if not self.reference:
                        line = fid.readline()
                        self.reference = [ float(r) for r in line.split()]
                    continue

                if line[:17] == '[number of ports]':
                    self.rank = int(line.split()[-1])
                    continue

                if line[:23] == '[number of frequencies]':
                    self.frequency_nb = line.split()[-1]
                    continue

                if line[:14] == '[network data]':
                    continue

                if line[:5] == '[end]':
                    continue

                if line[0] == '#':
                    toks = line[1:].strip().split()
                    toks.extend(['ghz', 's', 'ma', 'r', '50'][len(toks):])
                    self.frequency_unit = toks[0]
                    self.parameter = toks[1]
                    self.format = toks[2]
                    self.resistance = complex(toks[4])
                    if self.frequency_unit not in ['hz', 'khz', 'mhz', 'ghz']:
                        print('ERROR: illegal frequency_unit [%s]',  self.frequency_unit)
                    if self.parameter not in 'syzgh':
                        print('ERROR: illegal parameter value [%s]', self.parameter)
                    if self.format not in ['ma', 'db', 'ri']:
                        print('ERROR: illegal format value [%s]', self.format)

                    continue

                values.extend([ float(v) for v in line.split() ])

            values = numpy.asarray(values)
            if self.rank == 2:
                pos = numpy.where(numpy.sign(numpy.diff(values[::9])) == -1)
                if len(pos[0]) != 0:
                    pos = pos[0][0] + 1  
                    noise_values = values[pos*9:]
                    values = values[:pos*9]
                    self.noise = noise_values.reshape((-1,5))

            if len(values)%(1+2*(self.rank)**2) != 0 :
                raise AssertionError

            self.sparameters = values.reshape((-1, 1 + 2*self.rank**2))
            self.frequency_mult = {'hz':1.0, 'khz':1e3,
                                'mhz':1e6, 'ghz':1e9}.get(self.frequency_unit)

            if not self.reference:
                self.reference = [self.resistance] * self.rank

    def get_gamma_z0_from_fid(self, fid: typing.TextIO) -> None:
        gamma = []
        z0 = []

        def line2ComplexVector(s):
            """
            Принимает строку s и возвращает вектор комплексных чисел
            Вначале пробелы заменяются на один пробел, затем строка s разбивается на элементы через пробел
            Создается список из элементов, которые не являются пустыми строками (если таковые имеются)
            Оставшиеся элементы списка обрезаются так, чтобы остались только элементы, соответствующие вектору комплексных чисел
            Создается одномерный массив из этих элементов, и он преобразуется в вектор комплексных чисел с помощью функции scalar2Complex()
            """
            return self.scalar2Complex(npy.array([k for k in s.strip().split(' ')
                                                if k != ''][self.rank*-2:],
                                                dtype='float'))
            
        fid.seek(0)
        while True:
            line = fid.readline()
            if not line:
                break
            line = line.replace('\t', ' ')

            # если строка содержит Gamma, то добавляем гамму в массив
            if '! Gamma' in line:
                _line = line.replace('! Gamma', '').replace('!', '').rstrip()

                nb_elem = len(_line.split())

                if nb_elem == 2*self.rank:

                    gamma.append(line2ComplexVector(_line.replace('!', '').rstrip()))
                else:
                    for _ in range(int(npy.ceil(self.rank/4.0)) - 1):
                        _line += fid.readline().replace('!', '').rstrip()
                    gamma.append(line2ComplexVector(_line))

            # если строка содержит Port Impedance, то добавляем z0 в массив
            if '! Port Impedance' in line:
                _line = line.replace('! Port Impedance', '').rstrip()
                nb_elem = len(_line.split())

                if nb_elem == 2*self.rank:
                    z0.append(line2ComplexVector(_line.replace('!', '').rstrip()))
                else:
                    for _ in range(int(npy.ceil(self.rank/4.0)) - 1):
                        _line += fid.readline().replace('!', '').rstrip()
                    z0.append(line2ComplexVector(_line))

         # если массив z0 пустой, то задаем значения по умолчанию
        if len(z0) == 0:
            z0 = npy.array(self.resistance, dtype=complex)

        self.gamma = npy.array(gamma)
        self.z0 = npy.array(z0)

    def scalar2complex(s: typing.List[typing.Union[float, int]]) -> npy.ndarray:
        """
        Преобразует список скалярных чисел в массив комплексных чисел.

        Аргументы:
        - s (List[Union[float, int]]): список, содержащий скалярные числа.

        Возвращает:
        - npy.ndarray: одномерный массив комплексных чисел, полученный из входного списка.
        """
        s = npy.array(s)
        z = []

        # Проходимся по каждой второй паре элементов списка s и формируем из них комплексные числа
        for k in range(0, len(s), 2):
            z.append(s[k] + 1j * s[k + 1])

        return npy.array(z).flatten()

    def get_sparameter_arrays(self) -> typing.Tuple[npy.ndarray, npy.ndarray]:
        """Извлекает значения комплексных параметров"""
        v = self.sparameters

        # Проверяем формат данных и переводим в комплексную форму
        if self.format == 'ri':  # Данные представлены как действительная и мнимая части
            v_complex = v[:,1::2] + 1j * v[:,2::2]
        elif self.format == 'ma':  # Данные представлены как модуль и фаза
            v_complex = v[:,1::2] * numpy.exp(1j * numpy.pi/180 * v[:,2::2])
        elif self.format == 'db':  # Данные представлены в децибелах и фазе
            v_complex = (10**(v[:,1::2]/20.0)) * numpy.exp(1j * numpy.pi/180 * v[:,2::2])

        # Возвращаем массив частот и массив комплексных s-параметров
        if self.rank == 2:
            # Решейпим комплексные s-параметры из (n, 4) в (n, 2, 2)
            # Транспонируем массив, чтобы поменять порядок входов и выходов
            return (v[:,0] * self.frequency_mult,
                    numpy.transpose(v_complex.reshape((-1, self.rank, self.rank)), axes=(0,2,1)))
        else:
            # Решейпим комплексные s-параметры из (n, 2) в (n, 1, 2)
            return (v[:,0] * self.frequency_mult,
                    v_complex.reshape((-1, self.rank, self.rank)))
                    
    def complex_2_magnitude(self, z: complex) -> float:
        """Преобразует комплексное число z в его модуль (вещественное неотрицательное число)."""
        return npy.abs(z)

    def magnitude_2_db(self, z: float) -> float:
        """Преобразует амплитуду z в децибелы."""
        return 20 * npy.log10(z)

    def complex_2_db(self, z: complex) -> float:
        """Преобразует комплексное число z в децибелы."""
        return self.magnitude_2_db(npy.abs(z))

    def complex_2_degree(self, z: complex) -> float:
        """Преобразует комплексное число z в градусы."""
        return npy.angle(z, deg=True)

    def complex_2_radian(self, z: complex) -> float:
        """Преобразует комплексное число z в радианы."""
        return npy.angle(z)
        
    def complex_2_real(self, z: complex) -> float:
        """Возвращает действительную часть комплексного числа z."""
        return npy.real(z)

    def complex_2_imag(self, z: complex) -> float:
        """Возвращает мнимую часть комплексного числа z."""
        return npy.imag(z)

    def create_plot(self) -> None:
        # Создаем папку, если ее не существует, для хранения EM файлов.
        em_path = os.path.join(RAW_PATH_TO_KLAYOUT, "EM")
        if not os.path.exists(em_path):
            os.mkdir(em_path)

        # Получаем частоту и S-параметры из данных.
        freq, sparameter = self.get_sparameter_arrays()

        # Создаем текстовый файл и записываем в него значения частоты и значения, соответствующие графику.
        txt_file = open(os.path.join(em_path, "gnuplotData.txt"), "w+")
        if self.plot_type in ("MAG", "DB", "ANG", "RAD", "RE", "IM"):
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                val = self._get_plot_value(sparameter[i][self.from_port - 1][self.to_port - 1], self.plot_type)
                txt_file.write(f"{val}\n")
            txt_file.close()

            # Создаем строку gnuplot и записываем ее в процесс для построения графика.
            ylabel = self._get_plot_ylabel(self.plot_type)
            gnuplot_str = f"set grid\nset ylabel\"{ylabel}\"\nset xlabel\"Frequency (GHz)\"\nplot \"{txt_file.name.replace(os.sep, '/')}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())

    def _get_plot_value(self, sparameter_val: complex, plot_type: str) -> float:
        """
        Конвертирует значение S-параметра в значение для отображения на графике.

        Аргументы:
        - sparameter_val (complex): Значение S-параметра, которое необходимо сконвертировать.
        - plot_type (str): Тип значения для отображения на графике. Может быть одним из значений:
                           "MAG", "DB", "ANG", "RAD", "RE", "IM".

        Возвращает:
        - float: Конвертированное значение для отображения на графике.
        """
        if plot_type == "MAG":
            return self.complex_2_magnitude(sparameter_val)
        elif plot_type == "DB":
            return self.complex_2_db(sparameter_val)
        elif plot_type == "ANG":
            return self.complex_2_degree(sparameter_val)
        elif plot_type == "RAD":
            return self.complex_2_radian(sparameter_val)
        elif plot_type == "RE":
            return self.complex_2_real(sparameter_val)
        elif plot_type == "IM":
            return self.complex_2_imag(sparameter_val)

    def _get_plot_ylabel(self, plot_type: str) -> str:
        """
        Возвращает подпись для оси y на графике в зависимости от типа графика.

        Аргументы:
        - plot_type (str): Тип графика. Может быть одним из значений: "MAG", "DB", "ANG", "RAD", "RE", "IM".

        Возвращает:
        - str: Подпись для оси y на графике.
        """
        if plot_type in ("MAG", "DB"):
            return "Magnitude" if plot_type == "MAG" else "Magnitude (dB)"
        elif plot_type == "ANG":
            return "Phase (Deg)"
        elif plot_type == "RAD":
            return "Phase (Rad)"
        elif plot_type == "RE":
            return "Real"
        elif plot_type == "IM":
            return "Imag"


