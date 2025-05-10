# Copyright (c) 2020, Build-A-Cell. All rights reserved.
# See LICENSE file in the project root directory for details.

from unittest import TestCase
from biocrnpyler import Species, Compartment
from biocrnpyler import Mixture, ChemicalReactionNetwork
from biocrnpyler.components.dna import ActivatablePromoter, DNAassembly
from biocrnpyler.mixtures import EnergyTxTlExtract
import tempfile
import os
import libsbml


class TestSpecies(TestCase):
    def test_compartment_initialization(self):
        # tests naming convention repr without species type or attributes
        species = Species(name='test_species')
        compartment = Compartment(name='test_compartment')
        species.compartment = compartment
        self.assertEqual(compartment.name, 'test_compartment')
        self.assertEqual(species.compartment.name, compartment.name)

        # Test non-string named compartment
        with self.assertRaisesRegex(ValueError, 'Compartment name must be a string.'):
            compartment = Compartment(name = 24)

        with self.assertRaisesRegex(TypeError, 'Compartment name must be a string.'):
            compartment = Compartment(name = "test_compartment")
            compartment.name = None

        # tests naming convention for species with name and compartment
        compartment = Compartment(
            name='test_compartment', spatial_dimensions=1, size=1e-4)
        self.assertEqual(compartment.spatial_dimensions, 1)
        self.assertEqual(compartment.size, 1e-4)
        with self.assertRaises(ValueError):
            Compartment(name='2test_compartment')

        with self.assertRaisesRegex(ValueError, 'Compartment name must be a string'):
            compartment = Compartment(name="test_compartment")
            compartment.name = 24

        with self.assertRaisesRegex(ValueError, 'Compartment size must be a float or int.'):
            Compartment(name="test_compartment", size='2.5')

        with self.assertRaisesRegex(ValueError, 'Compartment size must be non-negative.'):
            Compartment(name="test_compartment", size=-2)

        with self.assertRaisesRegex(ValueError, 'Compartment spatial dimension must be an integer.'):
            Compartment(name="test_compartment", spatial_dimensions=2.5)

        with self.assertRaisesRegex(ValueError, 'Compartment spatial dimension must be non-negative.'):
            Compartment(name="test_compartment", spatial_dimensions=-2)

        with self.assertRaisesRegex(ValueError, 'Compartments with same names must have the same size and spatial dimensions.'):
            compartment1 = Compartment(
                name="test_compartment", spatial_dimensions=2)
            compartment2 = Compartment(
                name="test_compartment", spatial_dimensions=3)
            self.assertEqual(compartment1, compartment2)
        compartment = Compartment(name="test_compartment", unit="litre")
        self.assertEqual(compartment.unit, "litre")
        compartment.unit = "nanolitre"
        self.assertEqual(compartment.unit, "nanolitre")
        with self.assertRaisesRegex(ValueError, 'Unit of compartment must be a string representing compartment size.'):
            compartment = Compartment(name="test_compartment")
            compartment.unit = 24

        compartment = Compartment(name="test_compartment")
        self.assertEqual(compartment.unit, None)
    
    def test_compartment_in_sbml(self):
        """Test that compartment setting works correctly and 
        persists through SBML export/import"""
        comp1 = Compartment(name="comp1")
        s1 = Species("S1", compartment=comp1)
        mixture_1 = Mixture(species=[s1])
        crn_1 = mixture_1.compile_crn()
        self.assertEqual(s1.compartment.name, "comp1")
        # write sbml
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            crn_1.write_sbml_file(tmp.name)
            model = libsbml.readSBMLFromFile(tmp.name).getModel()
            sbml_species = model.getSpecies(0)
            self.assertEqual(sbml_species.getCompartment(), "comp1")
        os.remove(tmp.name)
        
    def test_compartment_setter(self):
        """Test that compartment setting works correctly and 
        persists through SBML export/import"""
        comp1 = Compartment(name="comp1")
        comp2 = Compartment(name="comp2") 

        s1 = Species("S1", compartment=comp1)
        mixture_1 = Mixture(species=[s1])
        crn_1 = mixture_1.compile_crn()
        crn_1.write_sbml_file("test_compartment_setter_1.xml")
        # change compartment
        s1.compartment = comp2
        mixture_2 = Mixture(species=[s1])
        crn_2 = mixture_2.compile_crn()
        self.assertEqual(s1.compartment.name, "comp2")
        
        # with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
        # crn_2.write_sbml_file(tmp.name)
        crn_2.write_sbml_file("test_compartment_setter_2.xml")
        model = libsbml.readSBMLFromFile("test_compartment_setter_2.xml").getModel()
        sbml_species = model.getSpecies(0)
        self.assertEqual(sbml_species.getCompartment(), "comp2")
            
        # os.unlink(tmp.name)
    def test_compartment_in_special_mixtures(self):
        activatable_assembly = DNAassembly(name="activatable_assembly", 
                                           promoter=ActivatablePromoter(name="activatable_promoter"))
        E = EnergyTxTlExtract(components=[activatable_assembly],
                              parameter_file = "../../../default_parameters.txt")
        self.assertEqual(E.rnap.species.compartment.name, "default")
        E.rnap.species.compartment = Compartment(name="Internal_0")
        CRN = E.compile_crn() #comple CRN
        self.assertEqual(E.rnap.species.compartment.name, "Internal_0")
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            CRN.write_sbml_file(tmp.name)
            model = libsbml.readSBMLFromFile(tmp.name).getModel()
            sbml_species = model.getSpecies(0)
            self.assertEqual(sbml_species.getCompartment(), "Internal_0")
        os.remove(tmp.name)
        



