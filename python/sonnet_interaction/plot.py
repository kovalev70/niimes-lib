import typing
import numpy
import numpy as npy
import math
import pya
import os
RAW_PATH_TO_KLAYOUT = r"{}".format(os.getcwd())

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
    
    def get_fid(self, file, *args, **kwargs):
        if isinstance(file, str):
            return open(file, *args, **kwargs)
        else:
            return file

    def load_file(self, fid: typing.TextIO):
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

    def get_gamma_z0_from_fid(self, fid):
        gamma = []
        z0 = []
        def line2ComplexVector(s):
            return self.scalar2Complex(npy.array([k for k in s.strip().split(' ')
                                                if k != ''][self.rank*-2:],
                                                dtype='float'))
        fid.seek(0)
        while True:
            line = fid.readline()
            if not line:
                break
            line = line.replace('\t', ' ')

            if '! Gamma' in line:
                _line = line.replace('! Gamma', '').replace('!', '').rstrip()

                nb_elem = len(_line.split())

                if nb_elem == 2*self.rank:

                    gamma.append(line2ComplexVector(_line.replace('!', '').rstrip()))
                else:
                    for _ in range(int(npy.ceil(self.rank/4.0)) - 1):
                        _line += fid.readline().replace('!', '').rstrip()
                    gamma.append(line2ComplexVector(_line))


            if '! Port Impedance' in line:
                _line = line.replace('! Port Impedance', '').rstrip()
                nb_elem = len(_line.split())

                if nb_elem == 2*self.rank:
                    z0.append(line2ComplexVector(_line.replace('!', '').rstrip()))
                else:
                    for _ in range(int(npy.ceil(self.rank/4.0)) - 1):
                        _line += fid.readline().replace('!', '').rstrip()
                    z0.append(line2ComplexVector(_line))

        if len(z0) == 0:
            z0 = npy.array(self.resistance, dtype=complex)

        self.gamma = npy.array(gamma)
        self.z0 = npy.array(z0)

    def scalar2Complex(s):
        s = npy.array(s)
        z = []

        for k in range(0,len(s),2):
            z.append(s[k] + 1j*s[k+1])
        return npy.array(z).flatten()
   
    def get_sparameter_arrays(self):
        v = self.sparameters

        if self.format == 'ri':
            v_complex = v[:,1::2] + 1j* v[:,2::2]
        elif self.format == 'ma':
            v_complex = (v[:,1::2] * numpy.exp(1j*numpy.pi/180 * v[:,2::2]))
        elif self.format == 'db':
            v_complex = ((10**(v[:,1::2]/20.0)) * numpy.exp(1j*numpy.pi/180 * v[:,2::2]))

        if self.rank == 2 :
            return (v[:,0] * self.frequency_mult,
                    numpy.transpose(v_complex.reshape((-1, self.rank, self.rank)),axes=(0,2,1)))
        else:
            return (v[:,0] * self.frequency_mult,
                    v_complex.reshape((-1, self.rank, self.rank)))
                    
    def complex_2_magnitude(self, z):
        return npy.abs(z)
            
    def magnitude_2_db(self, z):
        return 20 * npy.log10(z)  
    
    def complex_2_db(self, z):
        return self.magnitude_2_db(npy.abs(z)) 
        
    def complex_2_degree(self, z):
        return npy.angle(z, deg=True)
    
    def complex_2_radian(self, z):
        return npy.angle(z)
        
    def complex_2_real(self, z):
        return npy.real(z)
        
    def complex_2_imag(self, z):
        return npy.imag(z)
           
    def create_plot(self):
        freq, sparameter = self.get_sparameter_arrays()
        txt_file = open(RAW_PATH_TO_KLAYOUT+ f"\EM\gnuplotData.txt", "w+")
        path_to_data = txt_file.name.replace('\\', '/')
        
        if (self.plot_type == "MAG"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                mag = self.complex_2_magnitude(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{mag}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Magnitude\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            print(gnuplot_str)
            self.process.write(gnuplot_str.encode())
            
        if (self.plot_type == "DB"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                db = self.complex_2_db(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{db}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Magnitude (dB)\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())
            
        if (self.plot_type == "ANG"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                ang = self.complex_2_degree(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{ang}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Phase (Deg)\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())
            
        if (self.plot_type == "RAD"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                rad = self.complex_2_radian(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{rad}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Phase (Rad)\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())
            
        if (self.plot_type == "RE"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                real = self.complex_2_real(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{real}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Real\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())
            
        if (self.plot_type == "IM"):             
            for i in range(len(sparameter)):
                txt_file.write(f"{freq[i]/1000000000} ")
                imag = self.complex_2_imag(sparameter[i][self.from_port - 1][self.to_port - 1])          
                txt_file.write(f"{imag}\n")
            txt_file.close()
            gnuplot_str = "set ylabel\"Imag\"\n" + "set xlabel\"Frequency (GHz)\"\n" + f"plot \"{path_to_data}\" u 1:2 with lines title \"S{self.from_port}{self.to_port}\" lt rgb \"red\"\n"
            self.process.write(gnuplot_str.encode())
